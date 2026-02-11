# Zero Cost AI Blog

This project is a fully automated blog system using:
- **Pelican**: Static Site Generator (Python)
- **GitHub Pages**: Free Hosting
- **Gemini 2.5 Flash**: AI Content Generation
- **Google GenAI SDK**: For communicating with Gemini

## Setup

1.  **Clone/Create Repo**:
    Ensure this folder is a Git repository and linked to GitHub.
    ```bash
    git init
    git remote add origin https://github.com/your-username/your-repo.git
    ```

2.  **Setup Environment**:
    You can run the included batch file to automatically set up the environment and run the tool:
    ```cmd
    run_blog.bat
    ```
    
    Or manually:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_actual_api_key_here
    ```

## Usage

Run the master script to generate a post, build the site, and deploy it:

```bash
# Windows
run_blog.bat

# Or manually
venv\Scripts\python auto_blog.py
```

### Manual Commands

- **Generate Content**: `python generate_post.py`
- **Build Site**: `pelican content`
- **Preview Locally**: `pelican --listen` (then go to http://localhost:8000)
- **Deploy**: `ghp-import output -b gh-pages -p -f`

## Customization

- **Theme**: You can install Pelican themes and set `THEME = 'path/to/theme'` in `pelicanconf.py`.
- **Settings**: Edit `pelicanconf.py` for site name, author, etc.
