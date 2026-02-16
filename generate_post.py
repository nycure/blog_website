import os
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # If not found in .env, check system environment variable as fallback
    api_key = os.environ.get("GEMINI_API_KEY")

pollen_api_key = os.getenv("POLLENAI_API_KEY")
unsplash_access_key = os.getenv("unplas_acces_key")

api_key2 = os.getenv("GEMINI_API_KEY2")
if not api_key2:
    api_key2 = os.environ.get("GEMINI_API_KEY2")

if not api_key:
    print("Error: GEMINI_API_KEY not found. Please set it in a .env file or as an environment variable.")
    exit(1)

# Global variable to track the currently working API key
active_api_key = api_key

def call_gemini_api(prompt, model="gemini-2.5-flash"):
    """
    Calls Gemini API with fallback support and persistence.
    """
    global active_api_key
    
    # Try with the currently active key
    client = genai.Client(api_key=active_api_key)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"   ⚠️ API call failed with current key: {e}")
        
        # If we are currently using the primary key and have a secondary one, switch.
        if active_api_key == api_key and api_key2:
            print("   🔄 Switching to secondary API key (and setting it as active)...")
            active_api_key = api_key2
            try:
                client2 = genai.Client(api_key=active_api_key)
                response = client2.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text
            except Exception as e2:
                print(f"   ❌ Secondary API key also failed: {e2}")
                return None
        else:
            print("   ❌ No other API keys to try or secondary key also failed.")
            return None

def generate_draft(topic):
    """
    Pass 1: Generates the initial draft.
    """
    print(f"   Drafting content for '{topic}'...")
    prompt = f"""
    You are an expert, versatile blog writer. You can write engaging, high-quality content on ANY topic, not just technology.
    
    Topic: "{topic}"
    
    Write a comprehensive, SEO-friendly blog post.
    
    Structure the response in the following format exactly:
    
    Title: [Catchy Title, max 50 characters]
    Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
    Category: [Most Relevant Category]
    Tags: [tag1], [tag2], [tag3]
    Slug: [seo-friendly-slug]
    Authors: Admin
    Summary: [Compelling meta description, max 160 chars]
    
    [Content of the blog post in Markdown]
    
    - Use H2 (##) and H3 (###) for structure.
    - Keep paragraphs short and readable.
    - If the topic is technical, use code blocks. If it's lifestyle/news, use emotive language.
    - Ensure a proper conclusion.
    """
    
    response_text = call_gemini_api(prompt)
    if response_text:
        return response_text
    else:
        print("   Error generating draft: All API attempts failed.")
        return None

def critique_and_fix(draft_content):
    """
    Pass 2: The Editor AI reviews and polished the draft.
    """
    print("   Reviewing and polishing (AI Editor Mode)...")
    
    prompt = f"""
    You are a strict Editor-in-Chief. Review the following blog post draft for quality, formatting, and impact.
    
    Your Goal: Return the FINAL, polished version of the post.
    
    Checklist:
    1. **Metadata**: Ensure Title, Date, Slug, etc. are at the very top, formatted correctly for Pelican.
    2. **Formatting**: Ensure Markdown is clean (no broken lists or unclosed bolds).
    3. **Tone**: Ensure the tone matches the topic (e.g., authoritative for tech, warm for travel).
    4. **Backlinks (CRITICAL)**: Analyze the content and identifying 3-5 key concepts, technologies, or news items mentioned. 
       - At the very end of the post, add a section titled "## Further Reading & Resources".
       - Add a bulleted list of ACTUAL, VALID URLs to authoritative sources (e.g., official documentation, Wikipedia, major news outlets) that support the article. 
       - Do NOT invent fake links. If you are unsure of a specific URL, link to the general domain or explain how to find it.
    5. **No Chatty Filler**: Do NOT include "Here is the corrected version" or "I fixed a typo". Just output the BLOG POST.
    
    --- DRAFT TO REVIEW ---
    {draft_content}
    --- END DRAFT ---
    """

    response_text = call_gemini_api(prompt)
    if response_text:
        return response_text
    else:
        print("   Error during review: All API attempts failed.")
        return draft_content  # Fallback to draft if review fails

def generate_featured_image(title, slug):
    """
    Generates a featured image for the blog post.
    3-Tier Fallback (no timeouts — only fallback on actual errors):
      Tier 1: Pollinations.ai API (AI-generated image)
      Tier 2: Unsplash API (real photo)
      Tier 3: Local Pillow Generation (gradient + text overlay)
    """
    filename = f"{slug}.webp"
    filepath = os.path.join("content", "images", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Check if image already exists (to avoid overwriting if re-running)
    if os.path.exists(filepath):
        print(f"   Image already exists: images/{filename}")
        return f"images/{filename}"

    print(f"   🖼️  Generating featured image for: {title}")

    # ═══════════════════════════════════════════════════
    # TIER 1: Pollinations.ai (AI-Generated Image)
    # ═══════════════════════════════════════════════════
    try:
        import urllib.parse
        prompt = f"{title}, high quality, detailed, 8k, futuristic, tech, abstract, clean"
        print(f"      [Tier 1] Pollinations.ai — prompt: '{prompt[:60]}...'")
        
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://gen.pollinations.ai/image/{encoded_prompt}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        if pollen_api_key:
            headers["Authorization"] = f"Bearer {pollen_api_key}"
            
        params = {"model": "flux", "width": 1200, "height": 630, "nologo": "true"}
        
        # No timeout — wait as long as needed, only fallback on errors
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200 and len(response.content) > 1000:
            image = Image.open(BytesIO(response.content))
            image.save(filepath, "WEBP", quality=80)
            print(f"      ✅ [Tier 1] AI image saved: images/{filename}")
            return f"images/{filename}"
        else:
            print(f"      ❌ [Tier 1] Failed. Status: {response.status_code}")
            
    except Exception as e:
        print(f"      ❌ [Tier 1] Pollinations.ai error: {e}")

    # ═══════════════════════════════════════════════════
    # TIER 2: Unsplash API (Real Photo)
    # ═══════════════════════════════════════════════════
    try:
        if unsplash_access_key:
            # Extract 2-3 keywords from the title for search
            keywords = " ".join(title.split()[:3])
            print(f"      [Tier 2] Unsplash API — searching: '{keywords}'")
            
            search_url = "https://api.unsplash.com/search/photos"
            params = {
                "query": keywords,
                "orientation": "landscape",
                "per_page": 1,
                "client_id": unsplash_access_key
            }
            
            # No timeout — wait as long as needed
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    image_url = data["results"][0]["urls"]["regular"]
                    print(f"      ✅ [Tier 2] Unsplash URL: {image_url[:60]}...")
                    # Return the URL directly (no download)
                    return image_url
                else:
                    print(f"      ❌ [Tier 2] No results found for '{keywords}'")
            else:
                print(f"      ❌ [Tier 2] Unsplash API failed. Status: {response.status_code}")
        else:
            print("      ⚠️  [Tier 2] Skipped — no Unsplash key found")
            
    except Exception as e:
        print(f"      ❌ [Tier 2] Unsplash error: {e}")

    # ═══════════════════════════════════════════════════
    # TIER 3: Local Pillow Fallback (Always Succeeds)
    # ═══════════════════════════════════════════════════
    print("      [Tier 3] Generating local gradient image...")
    try:
        width, height = 1200, 630
        
        # Modern Gradient Color Palettes
        colors = [
            ((41, 128, 185), (109, 213, 250)),   # Blue
            ((236, 0, 140), (252, 103, 103)),    # Red/Pink
            ((17, 153, 142), (56, 239, 125)),    # Green
            ((81, 74, 157), (36, 198, 220)),     # Purple/Cyan
            ((253, 29, 29), (252, 176, 69)),     # Orange
            ((30, 30, 30), (80, 80, 80)),        # Dark/Elegant
            ((0, 82, 136), (0, 195, 154)),       # Teal
        ]
        color_start, color_end = random.choice(colors)

        # Create gradient
        base = Image.new('RGB', (width, height), color_start)
        top_layer = Image.new('RGB', (width, height), color_end)
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top_layer, (0, 0), mask)

        # Draw Text
        draw = ImageDraw.Draw(base)
        
        # Font handling
        try:
            try:
                font = ImageFont.truetype("arialbd.ttf", 72)
            except:
                font = ImageFont.truetype("arial.ttf", 72)
        except:
            font = ImageFont.load_default()
            print("      Note: Using default font (system fonts not found).")

        # Wrap Text
        lines = textwrap.wrap(title, width=28)
        
        line_height = 85
        total_text_height = len(lines) * line_height
        y_text = (height - total_text_height) / 2
        
        for line in lines:
            try:
                left, top_b, right, bottom = draw.textbbox((0, 0), line, font=font)
                text_width = right - left
            except:
                text_width = draw.textlength(line, font=font)
                
            # Shadow effect for readability
            draw.text(((width - text_width) / 2 + 2, y_text + 2), line, font=font, fill=(0, 0, 0, 128))
            draw.text(((width - text_width) / 2, y_text), line, font=font, fill="white")
            y_text += line_height

        base.save(filepath, "WEBP", quality=80)
        print(f"      ✅ [Tier 3] Fallback image saved: images/{filename}")
        return f"images/{filename}"

    except Exception as e:
        print(f"      ❌ [Tier 3] Image generation completely failed: {e}")
        return None

def save_post(content, topic):
    """
    Saves the content to a file.
    """
    if not content:
        return

    # Extract slug
    slug = "new-post"
    for line in content.splitlines():
        if line.startswith("Slug:"):
            slug = line.replace("Slug:", "").strip()
            break
            
    # Sanitize slug
    slug = "".join([c for c in slug if c.isalnum() or c in "-_"]).lower()
    if not slug:
        slug = f"post-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Extract title from content for a better image prompt
    post_title = topic  # default to topic
    for line in content.splitlines():
        if line.startswith("Title:"):
            post_title = line.replace("Title:", "").strip()
            break
    
    # GENERATE FEATURED IMAGE (3-tier: Pollinations → Unsplash → Pillow)
    image_path = generate_featured_image(post_title, slug)
    
    # Inject Image metadata into the post if not already present
    if image_path and "Image:" not in content:
        lines = content.splitlines()
        new_lines = []
        injected = False
        for line in lines:
            new_lines.append(line)
            if line.startswith("Slug:") and not injected:
                new_lines.append(f"Image: {image_path}")
                injected = True
        
        if not injected:
            # Fallback: insert near the top
            new_lines.insert(0, f"Image: {image_path}")
             
        content = "\n".join(new_lines)

    filename = f"content/{slug}.md"
    os.makedirs("content", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Blog post saved to: {filename}")
    return filename

def generate_blog_post(topic):
    """
    Wrapper function for backward compatibility.
    Orchestrates the draft and critique process.
    """
    # Inner functions handle their own logging, so we don't need to print here.
    draft = generate_draft(topic)
    
    if not draft:
        return None
        
    final_content = critique_and_fix(draft)
    return final_content

if __name__ == "__main__":
    print("--- AI Blog Post Generator (Self-Correcting) ---")
    user_topic = input("Enter a topic: ")
    
    if user_topic:
        post_content = generate_blog_post(user_topic)
        if post_content:
            save_post(post_content, user_topic)
    else:
        print("No topic entered.")
