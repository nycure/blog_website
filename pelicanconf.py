from datetime import datetime
CURRENT_YEAR = datetime.now().year
AUTHOR = 'Analytics Drive'
SITENAME = 'Analytics Drive'
SITEURL = 'https://analyticsdrive.tech'

PATH = 'content'
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'

# --- THEME SETTINGS ---
THEME = 'themes/modern-ai'

# --- PLUGINS ---
PLUGIN_PATHS = ['plugins']
PLUGINS = ['sitemap', 'related_posts', 'feed_image']

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

# --- FEED SETTINGS ---
# Crucial for Google News & Aggregators
RSS_FEED_SUMMARY_ONLY = False
FEED_MAX_ITEMS = 50  # Control feed size

# --- SEO SETTINGS ---
SEO_DESCRIPTION = "Analytics Drive: Your futuristic guide to AI, Machine Learning, and Tech. Explore in-depth articles, tutorials, and insights on the future of innovation."
SEO_KEYWORDS = "AI, Machine Learning, Tech, Future, Python, Data Science, Neural Networks, Robotics, News"
OG_IMAGE = "images/blog.jpg" # Place image in content/images/

# --- UI CUSTOMIZATION ---
# Colors match the CSS variables in style.css
# You can override them here if you implement dynamic CSS injection, 
# but usually editing style.css is better.
HERO_TITLE = "AI, Tech & Future Innovation Blog"
HERO_SUBTITLE = "Musings on Artificial Intelligence & Code"

# --- NAVIGATION ---
# Main Menu
MENUITEMS = (
    ('Home', '/'),
    ('Archives', '/archives.html'),
    ('Categories', '/categories.html'),
    ('About', '/about/'),
)

# Social Links
SOCIAL = (
    ('Twitter', 'https://twitter.com/analyticsdrive'),
    ('Facebook', 'https://www.facebook.com/profile.php?id=61588072082428'),
    ('Instagram', 'https://www.instagram.com/analyticsdrive'),
)

TWITTER_USERNAME = '@analyticsdrive'
GOOGLE_ANALYTICS = 'G-P1LT4885S9'

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
    'extra/llms.txt': {'path': 'llms.txt'},
    'extra/BingSiteAuth.xml': {'path': 'BingSiteAuth.xml'},
    'extra/decd7afbea4543c78251f2c1a29d33c9.txt': {'path': 'decd7afbea4543c78251f2c1a29d33c9.txt'},
}

# Add current year to context
import datetime
CURRENT_YEAR = datetime.datetime.now().year
