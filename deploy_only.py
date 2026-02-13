import os
import sys
import subprocess

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
    print("   🚀 Manual Deploy Manager")
    print("========================================")
    
    # 1. Build
    print("\n[1/2] 🏗️  Rebuilding static site...")
    # Clean output first to be safe
    if os.path.exists("output"):
        try:
            import shutil
            shutil.rmtree("output")
        except:
            pass
            
    if not run_command("pelican content -s publishconf.py"):
        print("❌ Build failed.")
        return

    # 2. Deploy
    print("\n[2/2] 🚀 Deploying to GitHub Pages...")
    
    # Push to gh-pages branch
    if run_command("ghp-import output -b gh_pages -n -p -f"):
            print("\n✅ Success! Your changes are now live/updating on GitHub Pages.")
    else:
            print("\n❌ Deployment failed.")

if __name__ == "__main__":
    main()
    input("\nPress any key to close...")
