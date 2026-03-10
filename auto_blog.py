import os
import sys
import subprocess
from generate_post import generate_blog_post, save_post


def run_command(command):
    """Run a shell command."""
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        return False
    return True

def main():
    print("========================================")
    print("   🤖 AI Auto-Blog Manager")
    print("========================================")
    
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
        print(f"\n[1/3] 🧠 Generating content for '{topic}' using Gemini 2.5 Flash...")
        content = generate_blog_post(topic, use_grounding=use_grounding)
        if content:
            saved_file = save_post(content, topic)
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
        else:
            print("\n❌ Deployment failed.")
    else:
        print("Deployment skipped.")

if __name__ == "__main__":
    main()
