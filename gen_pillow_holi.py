from PIL import Image, ImageDraw, ImageFont
import math

# Create a vibrant gradient background
width, height = 1200, 630 # Standard OG image size
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Background: Smooth multi-color gradient (Holi Vibes)
for y in range(height):
    for x in range(width):
        r = int(255 * (math.sin(x / 300) + 1) / 2)
        g = int(255 * (math.sin(y / 200 + 2) + 1) / 2)
        b = int(255 * (math.sin((x + y) / 200 + 4) + 1) / 2)
        # Shift colors towards pinks/oranges
        r = min(255, r + 100)
        draw.point((x, y), fill=(r, g, b))

# Add some solid circles (powder splatters)
splatters = [
    (100, 100, 150, (233, 30, 99)),
    (1000, 500, 200, (0, 188, 212)),
    (200, 450, 120, (255, 152, 0)),
    (1100, 100, 180, (76, 175, 80)),
    (600, 50, 100, (136, 14, 79))
]

for cx, cy, radius, color in splatters:
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=color)

# Add text
text_main = "Happy Holi!"
text_sub = "Click to see your magical greeting!"

# Use bounding boxes to center without external fonts (if possible)
# Actually, since we want large text, let's load a default font and scale it, or try to load Arial/Segoe.
try:
    font_main = ImageFont.truetype("arialbd.ttf", 120)
    font_sub = ImageFont.truetype("arial.ttf", 40)
except:
    try:
        font_main = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 120)
        font_sub = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 40)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

# Function to center text
def get_text_dimensions(text_string, font):
    # Depending on Pillow version
    try:
        ascent, descent = font.getmetrics()
        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent
        return (text_width, text_height)
    except:
        # Fallback
        return (len(text_string)*60, 100) # very rough

try:
    # Try calculating exact bounds
    bbox_main = draw.textbbox((0,0), text_main, font=font_main)
    w_main = bbox_main[2] - bbox_main[0]
    h_main = bbox_main[3] - bbox_main[1]
    
    bbox_sub = draw.textbbox((0,0), text_sub, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
except:
    w_main = 600
    h_main = 100
    w_sub = 400

# Draw main text shadow
draw.text(((width - w_main) / 2 + 5, height / 2 - h_main - 20 + 5), text_main, font=font_main, fill=(0,0,0,100))
# Draw main text
draw.text(((width - w_main) / 2, height / 2 - h_main - 20), text_main, font=font_main, fill=(255, 255, 255))

# Draw sub text
draw.text(((width - w_sub) / 2, height / 2 + 30), text_sub, font=font_sub, fill=(255, 255, 255))

# Save
image.save("content/images/holi-card.jpg", "JPEG")
print("Successfully generated local holi-card.jpg using Pillow!")
