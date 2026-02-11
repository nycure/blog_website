import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Run a shell command and print output."""
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        sys.exit(result.returncode)

def main():
    print("--- 🚀 Deploying Blog to GitHub Pages ---")

    # 1. Build the static site
    print("\n[1/3] Building static site with Pelican...")
    run_command("pelican content -s publishconf.py")

    # 2. Check if output directory exists
    if not os.path.exists("output"):
        print("Error: 'output' directory not found. Build failed.")
        sys.exit(1)

    # 3. Deploy using ghp-import
    print("\n[2/3] Pushing to gh-pages branch...")
    # -n: Include a .nojekyll file
    # -p: Push to remote
    # -f: Force push
    try:
        run_command("ghp-import output -n -p -f")
        print("\n✅ Successfully deployed to GitHub Pages!")
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        print("Ensure you have set up a GitHub repository and have push access.")

if __name__ == "__main__":
    main()
