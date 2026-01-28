from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlmodel import select, Session
from app.models import get_session
from app.models.table.user import User
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, session: Session = Depends(get_session)):
    # Check if user exists
    statement = select(User).where(User.email == user.email)
    existing_user_result = await session.execute(statement)
    existing_user = existing_user_result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.email})
    refresh_token, refresh_expires = create_refresh_token(data={"sub": new_user.email})
    
    # Store refresh token in database
    new_user.refresh_token = refresh_token
    new_user.refresh_token_expires = refresh_expires
    await session.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/signin", response_model=Token)
async def signin(user: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    result = await session.execute(statement)
    db_user = result.scalars().first()
    
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token, refresh_expires = create_refresh_token(data={"sub": db_user.email})
    
    # Store refresh token in database
    db_user.refresh_token = refresh_token
    db_user.refresh_token_expires = refresh_expires
    await session.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

from fastapi.security import OAuth2PasswordBearer
from app.utils.security import SECRET_KEY, ALGORITHM
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin")

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_token(token_request: RefreshTokenRequest, session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and validate refresh token
        payload = jwt.decode(token_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    # Verify refresh token matches stored token and hasn't expired
    from datetime import datetime, timezone
    if user.refresh_token != token_request.refresh_token:
        raise credentials_exception
    
    if user.refresh_token_expires and user.refresh_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token, refresh_expires = create_refresh_token(data={"sub": user.email})
    
    # Update stored refresh token
    user.refresh_token = new_refresh_token
    user.refresh_token_expires = refresh_expires
    await session.commit()
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
