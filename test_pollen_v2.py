import requests
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("POLLENAI_API_KEY")

prompt = "futuristic cyberpunk city with neon lights"
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
        print(f"Response: {response.text[:200]}")
        return False

print(f"--- Testing Pollinations.ai (Based on User Docs) ---")

# Test 1: image.pollinations.ai (Bearer Token)
print("\n1. Testing: image.pollinations.ai/prompt/{prompt} (Bearer Token)...")
try:
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    auth_headers = headers.copy()
    if api_key:
        auth_headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.get(url, headers=auth_headers)
    if response.status_code == 200:
        save_image(response, "pollen_image_bearer.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: image.pollinations.ai (Query Param)
print("\n2. Testing: image.pollinations.ai/prompt/{prompt}?key={key} (Query Param)...")
try:
    url = f"https://image.pollinations.ai/prompt/{prompt}?key={api_key}&model=flux&width=1024&height=1024&nologo=true"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        save_image(response, "pollen_image_query.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"Error: {e}")

# Test 3: gen.pollinations.ai (Alternative Host from docs)
print("\n3. Testing: gen.pollinations.ai/image/{prompt} (Bearer Token)...")
try:
    url = f"https://gen.pollinations.ai/image/{prompt}" # Note: path is /image/{prompt}
    auth_headers = headers.copy()
    if api_key:
        auth_headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.get(url, headers=auth_headers)
    if response.status_code == 200:
        save_image(response, "pollen_gen_bearer.jpg")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        if response.status_code in [403, 530]:
             # Try fallback to plain HTTP just in case HTTPS cert issues (unlikely but possible with weird DNS)
             pass
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
