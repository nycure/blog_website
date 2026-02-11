import os
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # If not found in .env, check system environment variable as fallback
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found. Please set it in a .env file or as an environment variable.")
    exit(1)

client = genai.Client(api_key=api_key)

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
    
    Title: [Catchy Title]
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
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"   Error generating draft: {e}")
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
    4. **No Chatty Filler**: Do NOT include "Here is the corrected version" or "I fixed a typo". Just output the BLOG POST.
    
    --- DRAFT TO REVIEW ---
    {draft_content}
    --- END DRAFT ---
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"   Error during review: {e}")
        return draft_content  # Fallback to draft if review fails

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
