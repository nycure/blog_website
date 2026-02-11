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

def generate_blog_post(topic):
    """
    Generates a blog post using Gemini 2.5 Flash.
    """
    prompt = f"""
    You are an expert technical blog writer. Write a comprehensive, engaging, and SEO-friendly blog post about: "{topic}".
    
    The output must utilize Markdown formatting.
    
    Structure the response in the following format exactly, so it can be used by Pelican:
    
    Title: [Catchy Title Here]
    Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
    Category: [Relevant Category]
    Tags: [tag1], [tag2], [tag3]
    Slug: [seo-friendly-slug-url]
    Authors: AI Writer
    Summary: [A concise meta description for SEO, max 160 characters]
    
    [Content of the blog post in Markdown]
    
    Ensure the content is informative, uses headings (##, ###), includes code snippets if relevant to the topic, and has a clear conclusion.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

def save_post(content, topic):
    """
    Saves the generated content to a markdown file in the content/ directory.
    """
    if not content:
        return

    # Extract slug for filename, or fallback to a timestamped filename
    slug = "new-post"
    for line in content.splitlines():
        if line.startswith("Slug:"):
            slug = line.replace("Slug:", "").strip()
            break
            
    # Sanitize slug a bit just in case
    slug = "".join([c for c in slug if c.isalnum() or c in "-_"]).lower()
    
    filename = f"content/{slug}.md"
    
    # Ensure content directory exists
    os.makedirs("content", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Blog post saved to: {filename}")

if __name__ == "__main__":
    print("--- AI Blog Post Generator ---")
    user_topic = input("Enter a topic for your new blog post: ")
    
    if user_topic:
        print(f"Generating post for '{user_topic}'... this may take a moment.")
        post_content = generate_blog_post(user_topic)
        save_post(post_content, user_topic)
    else:
        print("No topic entered. Exiting.")
