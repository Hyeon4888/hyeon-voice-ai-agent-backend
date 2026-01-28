import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def main():
    # Generate unique user
    unique_id = generate_random_string()
    email = f"test_{unique_id}@example.com"
    password = "secretpassword"
    name = f"Test User {unique_id}"

    print(f"Testing Auth with: {email}")

    # 1. Signup
    signup_data = {
        "name": name,
        "email": email,
        "password": password
    }
    
    print("1. Attempting Signup...")
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    
    token = None
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"Signup Successful! Token: {token[:20]}...")
    else:
        print(f"Signup Failed: {response.status_code} - {response.text}")
        # Try signin if user exists
        if response.status_code == 400:
             print("User might exist, trying signin...")

    # 2. Signin (if needed)
    if not token:
        signin_data = {
            "email": email,
            "password": password
        }
        print("2. Attempting Signin...")
        response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"Signin Successful! Token: {token[:20]}...")
        else:
            print(f"Signin Failed: {response.status_code} - {response.text}")
            return

    # 3. Get User Info
    print("3. Attempting Get User Info (/auth/me)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"Get User Info Successful! ID: {user_info.get('id')}, Name: {user_info.get('name')}, Email: {user_info.get('email')}")
    else:
        print(f"Get User Info Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
