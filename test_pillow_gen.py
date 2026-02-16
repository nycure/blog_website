from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import os

def generate_text_image(title, slug):
    # Dimensions
    width, height = 1200, 630
    
    # Modern Gradient Colors
    colors = [
        ((41, 128, 185), (109, 213, 250)), # Blue
        ((236, 0, 140), (252, 103, 103)),  # Red/Pink
        ((17, 153, 142), (56, 239, 125)),  # Green
        ((81, 74, 157), (36, 198, 220))    # Purple/Cyan
    ]
    color_start, color_end = random.choice(colors)

    # Create gradient background
    base = Image.new('RGB', (width, height), color_start)
    top = Image.new('RGB', (width, height), color_end)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)

    # Draw Text
    draw = ImageDraw.Draw(base)
    
    # Load Font (fallback to default if arial not found)
    try:
        font_path = "arial.ttf" # Windows default
        font = ImageFont.truetype(font_path, 80)
    except:
        font = ImageFont.load_default()

    # Wrap Text
    lines = textwrap.wrap(title, width=20)
    
    # Calculate text position
    y_text = height/2 - (len(lines) * 80 / 2)
    for line in lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        text_width = right - left
        text_height = bottom - top
        draw.text(((width - text_width) / 2, y_text), line, font=font, fill="white")
        y_text += text_height + 20

    filename = f"{slug}-featured.jpg"
    base.save(filename)
    print(f"Generated fallback image: {filename}")

if __name__ == "__main__":
    generate_text_image("The Future of AI is Here", "future-ai")
