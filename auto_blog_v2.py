import os
import sys
import subprocess
from generate_post import generate_blog_post, save_post, detect_topic_type, TOPIC_CONFIG


def run_command(command):
    """Run a shell command."""
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        return False
    return True


def print_social_snippets(title, slug, tags):
    """
    Prints ready-to-paste social media sharing snippets after a successful deploy.
    """
    site_url = "https://analyticsdrive.tech"
    article_url = f"{site_url}/{slug}/"
    # Build hashtags from tags (take first 4, strip spaces)
    hashtags = " ".join(
        f"#{t.strip().replace(' ', '')}" for t in (tags or [])[:4]
    )

    print("\n" + "=" * 55)
    print("   📣  READY-TO-SHARE SNIPPETS  📣")
    print("=" * 55)

    print(f"""
🐦 TWITTER / X:
{title} → {article_url}
{hashtags}
""")
    print(f"""📘 REDDIT:
Title : {title}
URL   : {article_url}
""")
    print(f"""💼 LINKEDIN:
📖 New article: {title}

Read the full post → {article_url}

{hashtags} #blog #analytics
""")
    print("=" * 55 + "\n")

def main():
    print("========================================")
    print("   🤖 AI Auto-Blog Manager (V2)")
    print("========================================")
    
    # 0. Ask for Media Type
    print("\n   Select Media Output:")
    print("   1. AI Generated Image (Default)")
    print("   2. Custom Video")
    print("   3. Custom Image")
    media_choice = input("   Choice (1-3) [1]: ").strip()
    
    media_type = None
    media_path = None
    
    if media_choice == '2':
        media_type = 'video'
        print("\n   🎥 Enter Video URL (YouTube/Vimeo) OR Local Path (e.g., videos/my-clip.mp4):")
        media_path = input("   > ").strip().strip('"').strip("'")
    elif media_choice == '3':
        media_type = 'image'
        print("\n   🖼️  Enter Image Path (e.g., images/my-photo.jpg or C:\\Users\\...\\photo.jpg):")
        media_path = input("   > ").strip().strip('"').strip("'")
    else:
        print("   🎨 Using: AI Generated Image")

    # 1. Ask for Mode
    print("\n   Choose Mode:")
    print("   1. Standard (Creative/General Knowledge)")
    print("   2. Latest (Google Search Grounded) - Best for news/current events")
    mode_choice = input("   Select mode (1/2) [1]: ").strip()
    
    use_grounding = False
    if mode_choice == '2':
        use_grounding = True
        print("   🌍 Mode: Latest (Grounding Enabled)")
    else:
        print("   🎨 Mode: Standard")

    # 2. Ask for topic
    topic = input("\nEnter a topic for your new blog post (or press Enter to skip generation): ").strip()
    
    if topic:
        # Detect topic type and allow override
        detected_type = detect_topic_type(topic)
        valid_types = list(TOPIC_CONFIG.keys())
        print(f"\n   🏷️  Auto-detected Topic Type: {detected_type}")
        print(f"   Available Types: {', '.join(valid_types)}")
        override = input(f"   Press Enter to accept '{detected_type}', or type another type: ").strip().upper()
        final_type = override if override in TOPIC_CONFIG else detected_type
        print(f"   ✅ Using Topic Type: {final_type}")

        print(f"\n[1/3] 🧠 Generating content for '{topic}' using Gemini 2.5 Flash...")
        content = generate_blog_post(topic, use_grounding=use_grounding, topic_type=final_type)
        if content:
            # Pass the media arguments to save_post
            saved_file = save_post(content, topic, media_type=media_type, media_path=media_path)
        else:
            print("❌ Failed to generate content. Aborting.")
            return
    else:
        print("Skipping content generation.")


    # 2. Build
    print("\n[2/3] 🏗️  Building static site...")
    # Clean output first to be safe
    if os.path.exists("output"):
        # simple cleanup for windows/linux
        try:
            import shutil
            shutil.rmtree("output")
        except:
            pass
            
    if not run_command("pelican content -s publishconf.py"):
        print("❌ Build failed.")
        return

    # 3. Deploy
    print("\n[3/3] 🚀 Deploying to GitHub Pages...")
    confirm = input("Are you sure you want to deploy to GitHub? (y/n): ").strip().lower()
    if confirm == 'y':
        # Push to gh-pages branch
        if run_command("ghp-import output -b gh_pages -n -p -f"):
            print("\n✅ Success! Your blog is now live/updating on GitHub Pages.")
            # Print social sharing snippets if we generated a post
            if topic:
                # Try to extract title/slug/tags from saved file for snippets
                try:
                    import glob, re
                    md_files = sorted(glob.glob("content/*.md"), key=os.path.getmtime, reverse=True)
                    art_title, art_slug, art_tags = topic, None, []
                    if md_files:
                        with open(md_files[0], "r", encoding="utf-8") as f:
                            for line in f:
                                l = line.strip()
                                if l.lower().startswith("title:"):
                                    art_title = l.split(":", 1)[1].strip()
                                elif l.lower().startswith("slug:"):
                                    art_slug = l.split(":", 1)[1].strip()
                                elif l.lower().startswith("tags:"):
                                    art_tags = [t.strip() for t in l.split(":", 1)[1].split(",")]
                                elif l == "":
                                    break
                    if art_slug:
                        print_social_snippets(art_title, art_slug, art_tags)
                except Exception as e:
                    print(f"   (Could not generate social snippets: {e})")
        else:
            print("\n❌ Deployment failed.")
    else:
        print("Deployment skipped.")


if __name__ == "__main__":
    main()
