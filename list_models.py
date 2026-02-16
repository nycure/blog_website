from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # try backup
    api_key = os.getenv("GEMINI_API_KEY2")

if not api_key:
    print("API Key not found.")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    for m in client.models.list():
        print(f"Name: {m.name}")
except Exception as e:
    print(f"Error: {e}")
