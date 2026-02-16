import requests
from io import BytesIO
from PIL import Image

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    print(f"Generating image from: {url}")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save("test_pollinations_image.jpg")
            print("Image generated and saved to test_pollinations_image.jpg")
            return "test_pollinations_image.jpg"
        else:
            print(f"Failed to generate image. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    generate_image("futuristic cyberpunk city with neon lights")
