from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found.")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Generating Holi Thumbnail Image with Gemini...")
    response = client.models.generate_images(
        model='gemini-2.0-flash-exp-image-generation',
        prompt='A beautiful, premium, festive Happy Holi greeting card template. Aesthetic Indian traditional vibe with vibrant Gulal powder splashes (pink, magenta, orange, turquoise) on a clean white textured background. Elegant design suitable for a web sharing preview card.',
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9" # Standard for Open Graph images
        )
    )

    if response.generated_images:
        image_bytes = response.generated_images[0].image.image_bytes
        image = Image.open(BytesIO(image_bytes))
        image.save("content/images/holi-card-thumbnail.jpg", "JPEG")
        print("Success! Image saved to content/images/holi-card-thumbnail.jpg")
    else:
        print("No image generated.")

except Exception as e:
    print(f"Error: {e}")
