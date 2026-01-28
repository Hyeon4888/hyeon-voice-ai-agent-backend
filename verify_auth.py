import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def main():
    # Generate unique user for testing
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
    # Using json parameter since the endpoint expects JSON body
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    
    if response.status_code == 200:
        print(f"Signup Successful! Token: {response.json().get('access_token')[:20]}...")
    else:
        print(f"Signup Failed: {response.status_code} - {response.text}")
        return

    # 2. Signin
    signin_data = {
        "email": email,
        "password": password
    }
    
    print("2. Attempting Signin...")
    response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
    
    if response.status_code == 200:
        print(f"Signin Successful! Token: {response.json().get('access_token')[:20]}...")
    else:
        print(f"Signin Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
