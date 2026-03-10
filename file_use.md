# Analytics Drive Blog - Project Structure & File Guide

This document outlines the purpose of every file and folder in the `blog_website` project, categorized by active usage vs. deprecated/testing files.

## 🗂️ Core Folders
| Folder | Status | Purpose |
|---|---|---|
| `content/` | **ACTIVE** | Stores all the raw Markdown (`.md`) files for blog posts, plus `images/` and `videos/` for media, and `pages/` for static pages like About/Contact. |
| `output/` | **ACTIVE** | The generated HTML static website built by Pelican. This folder is the one that actually gets pushed to GitHub Pages. |
| `themes/modern-ai/` | **ACTIVE** | The custom Newspaper-style Jinja2/CSS theme that styles the site. (All CSS edits must be made directly in `templates/base.html`). |
| `plugins/` | **ACTIVE** | Contains Pelican Python plugins (e.g., `sitemap`, `related_posts`, `feed_image`). |
| `.git/` | **ACTIVE** | The hidden folder that tracks version control history. |
| `__pycache__/` | Auto-generated | Compiled Python bytecode. Can be ignored. |
| `venv/` | **ACTIVE** | The isolated Python virtual environment containing installed packages (Pillow, Pelican, Gemini SDK, etc.). |

---

## ⚙️ Configuration Files
| File | Status | Purpose |
|---|---|---|
| `pelicanconf.py` | **ACTIVE** | Primary Pelican settings file (theme, plugins, URL routing, markdown extensions). Used for local generation. |
| `publishconf.py` | **ACTIVE** | Production Pelican settings overriding `pelicanconf.py` (e.g., absolute URLs, RSS generation). Used right before deploying to GitHub. |
| `.env` | **ACTIVE** | Hidden file containing your secret API keys (Gemini, Pollinations, Unsplash). |
| `.gitignore` | **ACTIVE** | Tells Git which files/folders to *never* upload to GitHub (e.g., `.env`, `venv/`, `.db`). |
| `requirements.txt` | **ACTIVE** | Lists all Python packages required to run the blog. Used if setting up on a new PC. |

---

## 🏃🏾 Active Workflow Scripts & Bats
These are the files you actually use day-to-day to run the blog.

| File | Status | Purpose |
|---|---|---|
| `generate_post.py` | **ACTIVE (Core)** | The heart of the AI automation. Contains all prompts, WebP image conversion, and Gemini API calls to write articles. |
| `auto_blog_v2.py` | **ACTIVE (Core)** | The new, fixed command-line interface that asks you for the topic and media type, then triggers `generate_post.py`. |
| `run_blog_v2.bat` | **ACTIVE (Core)** | The Windows shortcut script you double-click to launch `auto_blog_v2.py`. |
| `deploy_only.py` / `.bat` | **ACTIVE** | Minimal script to quickly build the site and push it to GitHub Pages without generating a new article. |
| `submit_indexing.py` / `.bat` | **ACTIVE** | Script to push new URLs to Google Search Console and Bing Webmaster IndexNow protocols for fast SEO discovery. |
| `run_auto_indexing.bat` | **ACTIVE** | Alternate version of the indexing script. |
| `indexing.db` | **ACTIVE** | SQLite database used by the indexing scripts to remember which URLs have already been submitted to Google/Bing. |
| `backup_source.py` / `.bat` | **ACTIVE** | Script to zip up the entire project folder (excluding output/venv) to protect against accidental deletion. |
| `api.json` | **ACTIVE** | Service account credentials downloaded from Google Cloud for the Indexing API. |
| `round-water-...json` | **ACTIVE** | Another Google Cloud service account key file used for authentication. |

---

## 🗑️ Obsolete / Deprecated Scripts (Safe to Delete)
These are older versions of scripts that were replaced by the `v2` architecture. They are no longer actively used, but kept as history.

| File | Status | Reason |
|---|---|---|
| `auto_blog.py` | Deprecated | The old version of the blog creator before we fixed media uploading, WebP conversion, and prompt architecture. |
| `run_blog.bat` | Deprecated | Launches the old `auto_blog.py`. |
| `deploy.py` | Deprecated | Replaced by `deploy_only` and the integrated deployment sequence in `auto_blog_v2.py`. |
| `update_older_posts.py` | Deprecated | A one-off script used temporarily to fix markdown formatting on older posts. |

---

## 🧪 Testing Playground (Safe to Delete)
These scripts were created temporarily during development to test specific APIs or libraries before integrating them into `generate_post.py`.

| File | Status | Reason |
|---|---|---|
| `test_pollen.py` / `_v2.py` / `_all.py` / `_final.py` | Testing | Sandbox scripts used to debug Pollinations.ai image generation failure blocks. |
| `test_pollinations.py` | Testing | Early API test for image generation. |
| `test_pillow_gen.py` | Testing | Sandbox script used to test creating fallback text-based images using the Python Pillow library. |
| `test_image_gen.py` | Testing | General script for testing Unsplash API and others before final integration. |
| `test_generation_flow.py` | Testing | Test script to check if the Gemini editor passes were working correctly without writing to disk. |
| `test_feedgenerator.py` | Testing | Sandbox for testing Pelican atom/RSS feed XML output. |
| `list_models.py` | Testing | Simple script to connect to the Gemini API and print available models (e.g., verifying `3.1-pro` access). |
| `pollen_final_bearer.jpg` / `_query.jpg` | Leftovers | Test images downloaded during the Pollinations.ai debugging phase. |

---

## 📝 Documentation
| File | Status | Purpose |
|---|---|---|
| `README.md` | **ACTIVE** | High-level repository overview. |
| `WORKFLOW.md` | **ACTIVE** | Internal AI rules and step-by-step instructions on how the blog is operated and maintained. |
| `file_use.md` | **ACTIVE** | This file! |
