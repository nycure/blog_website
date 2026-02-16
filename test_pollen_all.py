import requests
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("POLLENAI_API_KEY")

prompt = "futuristic cyberpunk city with neon lights"
base_url = f"https://image.pollinations.ai/prompt/{prompt}"

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
        return False

print(f"--- Testing Pollinations.ai with diverse methods ---")

# Method 1: Bearer Token
print("\n1. Testing with Bearer Token...")
try:
    auth_headers = headers.copy()
    if api_key:
        auth_headers["Authorization"] = f"Bearer {api_key}"
    response = requests.get(base_url, headers=auth_headers)
    if response.status_code == 200:
        save_image(response, "test_pollen_bearer.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Method 2: Query Parameter
print("\n2. Testing with Query Parameter (?key=)...")
try:
    url_with_key = f"{base_url}?nologo=true&private=true&key={api_key}" if api_key else base_url
    response = requests.get(url_with_key, headers=headers)
    if response.status_code == 200:
        save_image(response, "test_pollen_query.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Method 3: No Key (Free Tier)
print("\n3. Testing without Key (Free Tier)...")
try:
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        save_image(response, "test_pollen_free.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
