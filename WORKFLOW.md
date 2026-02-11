# Blog Workflow Guide

Here is the complete workflow for managing your "Zero Cost" AI Blog on GitHub Pages.

## 1. Prerequisites (Run Once)
- **Local Setup**: Run `run_blog.bat` once to install dependencies.
- **API Key**: Ensure your Gemini API Key is in `.env`.
- **GitHub**: Ensure your repo is connected (`git remote -v`).

## 2. Daily Workflow (Creating a Post)

Whenever you want to publish a new blog post:

1.  **Run the Automation Script**:
    Double-click `run_blog.bat` in the folder, or run it from the command line:
    ```cmd
    .\run_blog.bat
    ```

2.  **Enter a Topic**:
    The script will examine your current posts (if any) and ask: 
    `Enter a topic for your new blog post:`
    - Type a topic (e.g., "The Future of Quantum Computing").
    - Press Enter.
    
    > **Note**: The AI will generate a title, summary, tags, and content automatically.

3.  **Review (Optional)**:
    The script saves the post to `content/<slug>.md`.
    - To edit: You can open the `.md` file in any text editor before deploying.
    - If you edit it, just run `run_blog.bat` again later and press Enter (skip generation) to just build/deploy.

4.  **Confirm Deployment**:
    The script will ask: `Are you sure you want to deploy to GitHub? (y/n):`
    - Type `y` and Enter.
    - This pushes the built HTML to the `gh-pages` branch on GitHub.

## 3. SEO & Customization

You can now customize your blog's appearance and SEO settings from one place: `pelicanconf.py`.

### SEO Settings
Edit these variables in `pelicanconf.py` to change your site's metadata:
```python
SITENAME = 'My Tech Blog'
SEO_DESCRIPTION = "Expert insights on AI and programming."
SEO_KEYWORDS = "Python, AI, Tutorial, Tech"
TWITTER_USERNAME = "@nycure"
```

### UI Customization
You can change the hero text and colors:
```python
HERO_TITLE = "Welcome to the Future"
HERO_SUBTITLE = "Coding the impossible."
```
To change colors, edit `themes/modern-ai/static/css/style.css` and modify the `:root` variables at the top.

## 4. GitHub Pages Configuration (One-Time)

**Step 1: Setup Source**
1.  Go to your repository on GitHub.
2.  Settings > Pages > Build and deployment > **Deploy from a branch**.
3.  Branch: `gh-pages` / `/ (root)`.
4.  Save.

**Step 2: Custom Domain (Important)**
Because we added a `CNAME` file, GitHub might automatically detect your domain `analyticsdrive.tech`.
- Ensure "Custom domain" field says `analyticsdrive.tech`.
- Click **Enforce HTTPS** (might take 24h to become available).
- **DNS Setup**: You must go to your domain registrar (e.g., Namecheap, GoDaddy) and point your domain to GitHub Pages:
    - **A Record**: `@` -> `185.199.108.153` (and the other 3 GitHub IPs)
    - **CNAME Record**: `www` -> `nycure.github.io`
