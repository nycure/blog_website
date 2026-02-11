from datetime import datetime
CURRENT_YEAR = datetime.now().year
AUTHOR = 'Admin'
SITENAME = 'analyticsdrive'
SITEURL = ''

PATH = 'content'
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'

# --- THEME SETTINGS ---
THEME = 'themes/modern-ai'

# --- PLUGINS ---
# Sitemap is installed via pip, so we don't need PLUGIN_PATHS
PLUGINS = ['sitemap']

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.8,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

# --- SEO SETTINGS ---
SEO_DESCRIPTION = "A futuristic blog exploring AI, Technology, and Innovation."
SEO_KEYWORDS = "AI, Machine Learning, Tech, Future, Python"
OG_IMAGE = "images/blog.jpg" # Place image in content/images/

# --- UI CUSTOMIZATION ---
# Colors match the CSS variables in style.css
# You can override them here if you implement dynamic CSS injection, 
# but usually editing style.css is better.
HERO_TITLE = "Welcome into the Future"
HERO_SUBTITLE = "Musings on Artificial Intelligence & Code"

# --- NAVIGATION ---
# Main Menu
MENUITEMS = (
    ('Home', '/'),
    ('Archives', '/archives.html'),
    ('Categories', '/categories.html'),
)

# Social Links
SOCIAL = (
    ('GitHub', 'https://github.com/nycure'),
    ('Twitter', '#'),
)

DEFAULT_PAGINATION = 10
RELATIVE_URLS = True

# --- URL SETTINGS (Clean URLs) ---
ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

# --- STATIC & EXTRA PATHS ---
STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/CNAME': {'path': 'CNAME'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/android-chrome-192x192.png': {'path': 'android-chrome-192x192.png'},
    'extra/android-chrome-512x512.png': {'path': 'android-chrome-512x512.png'},
    'extra/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},
    'extra/favicon-16x16.png': {'path': 'favicon-16x16.png'},
    'extra/favicon-32x32.png': {'path': 'favicon-32x32.png'},
    'extra/site.webmanifest': {'path': 'site.webmanifest'},
}

# Add current year to context
import datetime
CURRENT_YEAR = datetime.datetime.now().year
