import requests
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("POLLENAI_API_KEY")

if not api_key:
    print("API Key POLLENAI_API_KEY not found.")
    exit(1)

def generate_image(prompt):
    # Try using the key as a query parameter
    # Note: Pollinations.ai search results suggest ?key= might work or ?token=
    url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true&private=true&key={api_key}"
    print(f"Generating image from: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save("test_pollen_image.jpg")
            print("Image generated and saved to test_pollen_image.jpg")
            return "test_pollen_image.jpg"
        else:
            print(f"Failed to generate image. Status: {response.status_code}")
            print(f"Response: {response.text[:200]}") # Print part of response for debugging
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    generate_image("futuristic cyberpunk city with neon lights")
