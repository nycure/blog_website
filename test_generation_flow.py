import generate_post
import sys

# Test the generation of a blog post
print("--- Testing Full Blog Post Generation Flow ---")
topic = "The Rise of Quantum Computing in 2026"
print(f"Topic: {topic}")

try:
    post_content = generate_post.generate_blog_post(topic)
    if post_content:
        filename = generate_post.save_post(post_content, topic)
        print(f"✅ Full flow successful. Saved to: {filename}")
        
        # Verify content
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if "Image:" in content:
                print("✅ Image metadata found.")
            else:
                print("❌ Image metadata MISSING!")
    else:
        print("❌ Failed to generate post content.")
except Exception as e:
    print(f"❌ Error: {e}")
