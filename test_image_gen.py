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
    print("Generating image...")
    # Using the Imagen 3 model via Gemini API (commonly accessed as imagen-3.0-generate-001 or similar)
    # The SDK 'models.generate_images' is the method for Image Generation API.
    # We need to confirm the correct model name. Let's try 'imagen-3.0-generate-001'.
    
    response = client.models.generate_images(
        model='gemini-2.0-flash-exp-image-generation',
        prompt='A futuristic city with flying cars and neon lights, digital art style',
        config=types.GenerateImagesConfig(
            number_of_images=1,
        )
    )

    if response.generated_images:
        image_bytes = response.generated_images[0].image.image_bytes
        image = Image.open(BytesIO(image_bytes))
        image.save("test_image.png")
        print("Image generated and saved to test_image.png")
    else:
        print("No image generated.")

except Exception as e:
    print(f"Error: {e}")
