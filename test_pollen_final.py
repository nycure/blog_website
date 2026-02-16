import requests
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("POLLENAI_API_KEY")

prompt = "a cat"
base_url = "https://gen.pollinations.ai"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def save_image(response, filename):
    try:
        image = Image.open(BytesIO(response.content))
        image.save(filename)
        print(f"✅ Image generated and saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to parse image. Content type: {response.headers.get('Content-Type')}")
        print(f"Response (first 200 chars): {response.text[:200]}")
        return False

print(f"--- Testing Pollinations.ai (Based on api.json) ---")
print(f"Server: {base_url}")

# Test 1: Models Discovery
print("\n1. Testing: /image/models...")
try:
    url = f"{base_url}/image/models"
    auth_headers = headers.copy()
    if api_key:
        auth_headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.get(url, headers=auth_headers, timeout=10)
    if response.status_code == 200:
        print(f"✅ Success! Models: {response.json()[:3]}...") # Print first 3 models
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Image Generation via API (Bearer Token)
print("\n2. Testing: /image/a%20cat?model=flux (Bearer Token)...")
try:
    url = f"{base_url}/image/a%20cat?model=flux"
    auth_headers = headers.copy()
    if api_key:
        auth_headers["Authorization"] = f"Bearer {api_key}"
    
    print(f"Requesting: {url}")
    response = requests.get(url, headers=auth_headers, timeout=30)
    if response.status_code == 200:
        save_image(response, "pollen_final_bearer.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Image Generation via Query Param
print("\n3. Testing: /image/a%20cat?key=... (Query Param)...")
try:
    url = f"{base_url}/image/a%20cat?model=flux&key={api_key}"
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        save_image(response, "pollen_final_query.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
