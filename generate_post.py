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

def clean_response(text):
    """
    Cleans the AI response by removing markdown code fences.
    """
    if not text:
        return text
        
    lines = text.splitlines()
    cleaned_lines = []
    inside_code_block = False
    
    # Check if the very first line is a code block marker
    if lines and lines[0].strip().startswith("```"):
        # simple stripping for the common case where the whole response is wrapped
        if lines[0].strip().startswith("```markdown"):
            lines = lines[1:]
        elif lines[0].strip() == "```":
            lines = lines[1:]
            
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
            
        return "\n".join(lines)
        
    return text

def call_gemini_api(prompt, model="gemini-2.5-flash", use_grounding=False):
    """
    Calls Gemini API with fallback support and persistence.
    """
    global active_api_key
    
    # Configure tools if grounding is requested
    config = None
    if use_grounding:
        print("   🌍 Using Google Search Grounding...")
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            response_modalities=["TEXT"]
        )

    # Try with the currently active key
    client = genai.Client(api_key=active_api_key)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
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
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e2:
                print(f"   ❌ Secondary API key also failed: {e2}")
                return None
        else:
            print("   ❌ No other API keys to try or secondary key also failed.")
            return None


def detect_topic_type(topic: str) -> str:
    """
    Detects the content type of the topic using keyword matching.
    Returns one of: TUTORIAL, NEWS, SPORTS, TECH_EXPLAINER, LISTICLE, REVIEW, GENERAL
    """
    t = topic.lower()

    # Tutorial / How-to
    if any(kw in t for kw in ["how to", "how do", "guide", "tutorial", "step by step", "steps to", "learn to", "build a", "write a", "create a"]):
        return "TUTORIAL"

    # Sports
    if any(kw in t for kw in ["match", "vs ", " v ", "tournament", "cricket", "football", "soccer", "tennis", "nba", "ipl", "t20", "world cup", "olympics", "race", "athlete", "league", "score", "game"]):
        return "SPORTS"

    # Listicle
    if any(kw in t for kw in ["top ", "best ", "worst ", "reasons ", " reasons", "tips for", "ways to", "must-have", " tools", " apps", "ranked"]):
        return "LISTICLE"

    # Review
    if any(kw in t for kw in ["review", "comparison", "pros and cons", " vs ", "worth it", "rating", "tested", "hands on", "hands-on"]):
        return "REVIEW"

    # Tech Explainer - removed "model", "release", "launch" (too generic)
    if any(kw in t for kw in ["what is", "explained", "how does", "deep dive", "understanding",
                               "overview of", "introduction to", "ai", "ml", "llm", "api",
                               "algorithm", "framework", "programming", "python", "javascript",
                               "neural", "blockchain", "cloud"]):
        return "TECH_EXPLAINER"

    # Entertainment / Film / Music (placed before TECH_EXPLAINER to prevent tech-bias)
    if any(kw in t for kw in ["trailer", "movie", "film", "cinema", "series", "episode",
                               "season", "actor", "actress", "director", "cast", "plot",
                               "marvel", "dc ", "netflix", "disney", "hbo", "anime",
                               "sequel", "prequel", "album", "song", "music video",
                               "concert", "celebrity", "tv show", "box office"]):
        return "ENTERTAINMENT"

    # News / Analysis
    if any(kw in t for kw in ["news", "breaking", "update", "latest", "announced", "release", "launch", "unveiled", "report", "analysis", "recap", "results", "impact", "2025", "2026"]):
        return "NEWS"

    return "GENERAL"


# Topic type config: min words, audience, style notes
TOPIC_CONFIG = {
    "TUTORIAL": {
        "min_words": 1800,
        "audience": "developer or student with beginner-to-intermediate knowledge",
        "style": "Use numbered steps for all procedures. Include code blocks where relevant. Use H3 for each step.",
        "structure": "Introduction → Prerequisites → Steps (numbered, H3) → Common Mistakes → Conclusion",
    },
    "NEWS": {
        "min_words": 1200,
        "audience": "general reader interested in current events",
        "style": "Use inverted pyramid structure (most important info first). Be factual, clear, and avoid speculation.",
        "structure": "Introduction (key facts) → Background Context → Key Details → Expert Opinion / Quotes → Impact → Conclusion",
    },
    "SPORTS": {
        "min_words": 1200,
        "audience": "passionate sports fan who follows the sport closely",
        "style": "Punchy, dynamic, journalistic. Use vivid language, statistics, and player highlights.",
        "structure": "Opening Hook → Match/Event Summary → Key Moments → Player Highlights → Stats & Standings → What It Means Going Forward → Conclusion",
    },
    "TECH_EXPLAINER": {
        "min_words": 1600,
        "audience": "tech-savvy reader aged 20-40 who wants depth, not fluff",
        "style": "Authoritative and informative. Use analogies for complex concepts. Back claims with data.",
        "structure": "Introduction → What Is It? → How It Works → Key Components / Features → Real-World Applications → Pros & Cons → Future Outlook → Conclusion",
    },
    "LISTICLE": {
        "min_words": 1400,
        "audience": "general reader looking for quick, actionable information",
        "style": "Use a numbered or bulleted list as the spine of the article. Each item must have 2-3 paragraphs of explanation.",
        "structure": "Introduction (why this list matters) → Numbered/Bulleted Items (H3 for each) → Honorable Mentions → Conclusion",
    },
    "REVIEW": {
        "min_words": 1500,
        "audience": "consumer or professional deciding whether to use/buy a product or service",
        "style": "Balanced and honest. Structure clearly around pros, cons, and verdict. Use a rating if appropriate.",
        "structure": "Introduction → What Is It? → Key Features → Performance & Testing → Pros → Cons → Who Should Use It? → Verdict",
    },
    "ENTERTAINMENT": {
        "min_words": 1200,
        "audience": "movie, TV, or music fan interested in pop culture and entertainment",
        "style": "Conversational, enthusiastic, fan-friendly tone. Focus on story, characters, cast, director, themes, and emotional impact. Do NOT write from a technology perspective. Write like an entertainment journalist or film critic.",
        "structure": "Opening Hook (hype/anticipation) → What Is It? (premise/franchise background) → Trailer or Announcement Breakdown → Cast & Director Highlights → Themes & Tone → Fan & Critic Reactions → Release Date & Where to Watch → Final Verdict / Excitement Level",
    },
    "GENERAL": {
        "min_words": 1500,
        "audience": "curious general reader",
        "style": "Engaging and informative. Mix facts with storytelling where appropriate.",
        "structure": "Introduction → Main Body (3-5 H2 sections) → Conclusion",
    },
}


def generate_draft(topic, topic_type="GENERAL", use_grounding=False):
    """
    Pass 1: Generates the initial draft using a topic-specific prompt.
    """
    print(f"   Drafting content for '{topic}' (Type: {topic_type})...")

    cfg = TOPIC_CONFIG.get(topic_type, TOPIC_CONFIG["GENERAL"])
    min_words = cfg["min_words"]
    audience = cfg["audience"]
    style = cfg["style"]
    structure = cfg["structure"]

    prompt = f"""You are an expert blog writer specializing in {topic_type.replace('_', ' ').title()} content.

Topic / Primary Keyword: "{topic}"
Content Type: {topic_type}
Target Audience: {audience}

Your Task: Write a comprehensive, SEO-optimized blog post on the above topic.

--- CRITICAL SEO REQUIREMENTS ---
1. TITLE: 55-60 characters. Include the primary keyword "{topic}" near the start. Make it compelling.
2. KEYWORD DENSITY: Use the primary keyword "{topic}" naturally:
   - Once in the first paragraph (intro)
   - At least once in an H2 heading
   - Once in the conclusion
   - Total: 3-5 times in the full article (do NOT overstuff)
3. H1 TITLE ALIGNMENT (CRITICAL FOR SEO): The Title you write becomes the H1 on the page.
   The FIRST PARAGRAPH of the body MUST naturally contain at least 3-4 meaningful words
   from that Title (ignore stopwords like "the", "a", "of", "and", "in", "to").
   Example: if Title is "ChatGPT vs Gemini: The Future of AI Assistants", the intro
   must mention words like "ChatGPT", "Gemini", "future", "AI assistants".
   This prevents the SEO warning: "Words from H1 heading not found in page content".
4. MINIMUM LENGTH: Write AT LEAST {min_words} words of body content. This is non-negotiable.
5. SUBHEADINGS: Use keyword-rich H2 and H3 headings that a reader might Google.

--- CONTENT STYLE ---
{style}

--- FORMATTING RULES ---
- NEVER wrap URLs in backticks (`https://example.com`). This breaks them.
- ALWAYS make links clickable using standard Markdown format: `[Link Text](https://example.com)`.

--- RECOMMENDED STRUCTURE ---
{structure}

--- OUTPUT FORMAT (Pelican Metadata at the very top, REQUIRED) ---
Title: [SEO title, 55-60 characters, keyword-first]
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Category: [Pick EXACTLY ONE from this fixed list — do NOT invent new categories:
  Artificial Intelligence | Technology | Algorithms | Data Structures |
  Competitive Programming | SQL & Databases | Cricket | Sports |
  Politics & Geopolitics | World News | Entertainment | Science & Space |
  India & Culture]
Tags: [Pick EXACTLY 3-4 tags from this fixed list ONLY — do NOT invent new tags:
  Python | Java | C Plus Plus | Algorithms | Data Structures | Dynamic Programming |
  Graph Theory | LeetCode | SQL | Competitive Programming | Artificial Intelligence |
  Technology | Machine Learning | Gemini | Cricket | Football | Sports | Olympics |
  India | Iran | USA | Pakistan | Geopolitics | World News | Movies | Entertainment |
  Marvel | Space | Science | Lifestyle]
Slug: [seo-friendly-slug-no-special-chars]
Authors: Admin
Summary: [Compelling meta description, exactly 150-160 characters, include keyword]

[Body content in Markdown starts here]

--- WRITING RULES ---
- **DOMAIN AWARENESS (CRITICAL)**: Write ENTIRELY from the perspective of the topic's own domain.
  - Movie/TV/trailer topic → write entertainment journalism (plot, cast, emotion, hype). NOT tech.
  - Food/travel topic → write lifestyle content. NOT tech.
  - Science topic → write science journalism. NOT software engineering.
  - NEVER default to a technology angle unless the topic itself is explicitly about technology.
- **CRITICAL — NO H1 HEADINGS**: Do NOT use `# Heading` (single `#`) anywhere in the body. The page template already displays the title as H1. Start sections with `## ` (H2) at minimum. Using H1 in the body creates a duplicate H1 which hurts SEO.
- NO filler phrases like "In conclusion, it is important to note..."
- Keep paragraphs to 3-4 sentences max.
- Use transition words between sections.
- Be specific — use real statistics, examples, and names where possible.
"""

    response_text = call_gemini_api(prompt, use_grounding=use_grounding)
    if response_text:
        return response_text
    else:
        print("   Error generating draft: All API attempts failed.")
        return None


def get_existing_posts(content_dir="content"):
    """
    Scans the content directory and returns a list of (title, slug) tuples
    for all existing posts. Used to inject internal linking opportunities
    into the editor AI prompt.
    """
    posts = []
    if not os.path.exists(content_dir):
        return posts
    for fname in os.listdir(content_dir):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(content_dir, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                title, slug = None, None
                for line in f:
                    line = line.strip()
                    if line.lower().startswith("title:"):
                        title = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("slug:"):
                        slug = line.split(":", 1)[1].strip()
                    elif line == "":
                        break  # End of metadata block
                if title and slug:
                    posts.append((title, slug))
        except Exception:
            continue
    return posts


def critique_and_fix(draft_content, topic, topic_type="GENERAL"):
    """
    Pass 2: The Editor AI reviews and polishes the draft.
    """
    print("   Reviewing and polishing (AI Editor Mode)...")

    cfg = TOPIC_CONFIG.get(topic_type, TOPIC_CONFIG["GENERAL"])
    min_words = cfg["min_words"]

    # --- Gather existing posts for internal linking ---
    existing_posts = get_existing_posts()
    if existing_posts:
        internal_links_block = "Available internal articles you can link to:\n"
        for title, slug in existing_posts[:40]:  # Cap at 40 to keep prompt lean
            internal_links_block += f"  - {title} → /{slug}/\n"
    else:
        internal_links_block = "(No existing articles found for internal linking.)"

    prompt = f"""You are a strict Editor-in-Chief reviewing a blog post draft. Your job is to return the FINAL, polished, publish-ready version.

Primary Keyword: "{topic}"
Content Type: {topic_type}
Minimum Required Word Count: {min_words} words

--- YOUR CHECKLIST ---

1. **METADATA** (CRITICAL): Ensure Title, Date, Category, Tags, Slug, Authors, Summary are at the very top. Pelican format, no changes to Date/Slug.

1b. **TAGS QUALITY** (CRITICAL): The Tags line must have EXACTLY 3-4 tags from this approved list (exact spelling required):
   Python, Java, C Plus Plus, Algorithms, Data Structures, Dynamic Programming,
   Graph Theory, LeetCode, SQL, Competitive Programming, Artificial Intelligence,
   Technology, Machine Learning, Gemini, Cricket, Football, Sports, Olympics,
   India, Iran, USA, Pakistan, Geopolitics, World News, Movies, Entertainment,
   Marvel, Space, Science, Lifestyle
   - Pick ONLY from this list. Replace any tag NOT on this list with the closest match.
   - No plural duplicates, no special characters.

1c. **SUMMARY LENGTH** (CRITICAL): Count the exact characters in the `Summary:` line. It MUST be exactly 150-160 characters. If it is 161+ characters, you MUST rewrite it to be shorter. Google truncates at 160.

1c. **CATEGORY QUALITY** (CRITICAL): The Category line must contain EXACTLY ONE value from this fixed list (exact spelling required):
   Artificial Intelligence, Technology, Algorithms, Data Structures,
   Competitive Programming, SQL & Databases, Cricket, Sports,
   Politics & Geopolitics, World News, Entertainment, Science & Space, India & Culture
   If the current Category is NOT on this list, replace it with the closest matching category from the list above.

2. **WORD COUNT**: Count the approximate words. If the body is under {min_words} words, EXPAND the weakest/shortest section by adding more detail, examples, or analysis. Do NOT remove content.

3. **KEYWORD USAGE**: Check that "{topic}" appears:
   - In the first paragraph
   - In at least one H2 heading  
   - In the conclusion
   If any are missing, add it naturally.

3b. **H1 TITLE ALIGNMENT** (SEO CRITICAL): Extract the exact Title from the metadata at the top.
    Check that the FIRST PARAGRAPH of the body contains at least 3-4 meaningful words from
    that Title (ignore stopwords: "the", "a", "of", "and", "in", "to", "for", "is", "are").
    If the first paragraph is missing key title words, rewrite its FIRST SENTENCE to naturally
    include them — do NOT change the rest of the paragraph.
    Example: Title "ChatGPT vs Gemini: The Future of AI" → intro must mention
    "ChatGPT", "Gemini", and "future" or "AI" naturally.

4. **FORMATTING**: Fix any broken Markdown (unclosed bolds, broken lists, inconsistent headings).
   - **CRITICAL**: If there are any URLs wrapped in backticks (like `https://...`), you MUST remove the backticks and convert them into standard clickable Markdown links: `[Text](https://...)`. Never leave a URL inside a code block.

5. **INTERNAL LINKS** (CRITICAL FOR SEO): Find 2-3 places in the body where you can naturally reference a related article from the list below. Insert a markdown link like `[anchor text](/slug/)`.
   - Use descriptive anchor text (NOT "click here" or "read more")
   - Only link where it is genuinely relevant — do NOT force it
   - Place links inside body paragraphs, NOT in headings

{internal_links_block}

6. **BACKLINKS**: At the very end, add a section:
   ## Further Reading & Resources
   List 3-5 REAL, VALID URLs to authoritative sources (Wikipedia, official docs, major news sites). NO fake or invented links.

7. **FAQ SECTION** (CRITICAL FOR SEO): Before "Further Reading", add:
   ## Frequently Asked Questions
   Write 3 realistic Q&A pairs a reader might Google about this topic. Format:
   **Q: [Question]**
   A: [Concise 2-3 sentence answer]

8. **NO CHATTY OUTPUT**: Do NOT write "Here is the revised version" or similar. Output ONLY the blog post.

--- DRAFT ---
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

def save_post(content, topic, media_type=None, media_path=None):
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
    
    # DETERMINE MEDIA (Custom Video/Image OR Default AI Image)
    image_path = None
    
    # inject_media_line will hold the string to inject, e.g. "Video: ..." or "Image: ..."
    inject_media_line = None

    if media_type == 'video' and media_path:
        # Handle Local Video Path vs URL
        if os.path.exists(media_path):
            # It's a local file, we need to copy it to content/videos
            import shutil
            video_filename = os.path.basename(media_path)
            # Ensure safe filename
            video_filename = "".join([c for c in video_filename if c.isalnum() or c in "-_."])
            
            target_dir = os.path.join("content", "videos")
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, video_filename)
            try:
                shutil.copy2(media_path, target_path)
                print(f"   📂 Copied video to: {target_path}")
                # Use relative path for Hugo/Pelican
                inject_media_line = f"Video: videos/{video_filename}"
                
                # --- THUMBNAIL GENERATION ---
                # Attempt to generate a thumbnail for OG:IMAGE
                try:
                    import subprocess
                    thumbnail_filename = f"{os.path.splitext(video_filename)[0]}_thumb.jpg"
                    images_dir = os.path.join("content", "images")
                    os.makedirs(images_dir, exist_ok=True)
                    thumbnail_path = os.path.join(images_dir, thumbnail_filename)
                    
                    # ffmpeg command to extract a frame at 00:00:01
                    cmd = [
                        "ffmpeg", "-y", "-i", target_path, 
                        "-ss", "00:00:01.000", "-vframes", "1", 
                        thumbnail_path
                    ]
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    if os.path.exists(thumbnail_path):
                        print(f"   📸 Generated thumbnail: {thumbnail_path}")
                        # Append Image metadata line
                        inject_media_line += f"\nImage: images/{thumbnail_filename}"
                except Exception as e:
                    print(f"   ⚠️ Could not generate thumbnail (ffmpeg missing?): {e}")

            except Exception as e:
                print(f"   ❌ Failed to copy video: {e}")
                inject_media_line = f"Video: {media_path}" # Fallback
        else:
            # Assume it's a URL (YouTube/Vimeo)
            print(f"   🎥 Using custom VIDEO URL: {media_path}")
            inject_media_line = f"Video: {media_path}"
            
            # TODO: Fetch YouTube/Vimeo thumbnail if possible, but complexity is high.
            # Ideally user provides one.
        
    elif media_type == 'image' and media_path:
        # Handle Local Image
        # Strip surrounding quotes (Windows drag-drop adds them)
        media_path = media_path.strip('"').strip("'")

        if os.path.exists(media_path):
            import shutil
            target_dir = os.path.join("content", "images")
            os.makedirs(target_dir, exist_ok=True)

            # --- WebP Conversion ---
            webp_filename = f"{slug}-hero.webp"
            target_webp = os.path.join(target_dir, webp_filename)
            converted = False
            try:
                from PIL import Image as PILImage
                img = PILImage.open(media_path)
                # Convert RGBA/P modes for WebP compat
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                # Resize to max 1200px wide
                max_w = 1200
                if img.width > max_w:
                    ratio = max_w / img.width
                    img = img.resize((max_w, int(img.height * ratio)), PILImage.LANCZOS)
                img.save(target_webp, "WEBP", quality=75, method=6)
                orig_kb = os.path.getsize(media_path) // 1024
                webp_kb  = os.path.getsize(target_webp) // 1024
                print(f"   🖼️  Converted to WebP: {target_webp}")
                print(f"   📦 Size: {orig_kb} KB → {webp_kb} KB (WebP)")
                inject_media_line = f"Image: images/{webp_filename}"
                converted = True
            except Exception as e:
                print(f"   ⚠️  WebP conversion failed ({e}), falling back to copy.")

            if not converted:
                # Fallback: plain copy without conversion
                image_filename = os.path.basename(media_path)
                image_filename = "".join([c for c in image_filename if c.isalnum() or c in "-_."])
                target_path = os.path.join(target_dir, image_filename)
                try:
                    shutil.copy2(media_path, target_path)
                    print(f"   📂 Copied image to: {target_path}")
                    inject_media_line = f"Image: images/{image_filename}"
                except Exception as e:
                    print(f"   ❌ Failed to copy image: {e}")
                    inject_media_line = None
        else:
            print(f"   ⚠️  Image file not found at: {media_path}")
            print(f"       Tip: Make sure the path exists and is not wrapped in quotes.")
            inject_media_line = None  # Fall back to AI image generation



    else:
        # Default Flow: Generate Featured Image
        # 3-tier: Pollinations → Unsplash → Pillow
        image_path = generate_featured_image(post_title, slug)
        if image_path:
            inject_media_line = f"Image: {image_path}"
    
    # Inject Media metadata into the post if not already present
    if inject_media_line:
        # Check if "Video:" or "Image:" is already in content (unlikely for new draft but good safety)
        if "Image:" not in content and "Video:" not in content:
            lines = content.splitlines()
            new_lines = []
            injected = False
            for line in lines:
                new_lines.append(line)
                if line.startswith("Slug:") and not injected:
                    new_lines.append(inject_media_line)
                    injected = True
            
            if not injected:
                # Fallback: insert near the top
                new_lines.insert(0, inject_media_line)
                 
            content = "\n".join(new_lines)

    filename = f"content/{slug}.md"
    os.makedirs("content", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Blog post saved to: {filename}")
    return filename

def generate_blog_post(topic, use_grounding=False, topic_type=None):
    """
    Wrapper function for backward compatibility.
    Orchestrates the draft and critique process.
    """
    # Auto-detect topic type if not provided
    if topic_type is None:
        topic_type = detect_topic_type(topic)
    print(f"   🏷️  Topic Type Detected: {topic_type}")

    draft = generate_draft(topic, topic_type=topic_type, use_grounding=use_grounding)
    
    if not draft:
        return None
        
    final_content = critique_and_fix(draft, topic=topic, topic_type=topic_type)
    return clean_response(final_content)

if __name__ == "__main__":
    print("--- AI Blog Post Generator (Self-Correcting) ---")
    print("   1. Standard")
    print("   2. Latest (Grounding)")
    mode = input("   Select mode (1/2) [1]: ").strip()
    use_grounding = (mode == '2')
    
    user_topic = input("Enter a topic: ")
    
    if user_topic:
        detected_type = detect_topic_type(user_topic)
        print(f"\n   🏷️  Auto-detected topic type: {detected_type}")
        valid_types = list(TOPIC_CONFIG.keys())
        override = input(f"   Press Enter to accept, or type a type {valid_types}: ").strip().upper()
        final_type = override if override in TOPIC_CONFIG else detected_type
        
        post_content = generate_blog_post(user_topic, use_grounding=use_grounding, topic_type=final_type)
        if post_content:
            save_post(post_content, user_topic)
    else:
        print("No topic entered.")
