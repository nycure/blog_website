"""
Feed Image Plugin for Pelican
------------------------------
Injects article featured images as <link rel="enclosure"> tags
into the Atom feed, so news aggregators (e.g. Brave News) can
display per-article thumbnails.
"""

from urllib.parse import urljoin

from feedgenerator import Enclosure
from pelican.writers import Writer

# Keep a reference to the original method
_original_add_item = Writer._add_item_to_the_feed

MIME_MAP = {
    'webp': 'image/webp',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'svg': 'image/svg+xml',
}


def _add_item_with_image(self, feed, item):
    """Wrapper that calls the original method, then appends an image
    enclosure if the article has an ``image`` metadata field."""
    _original_add_item(self, feed, item)

    if hasattr(item, 'image') and item.image:
        # Build absolute image URL
        if item.image.startswith('http'):
            image_url = item.image
        else:
            base = self.site_url
            image_url = urljoin(
                base if base.endswith('/') else base + '/',
                item.image,
            )

        # Determine MIME type from file extension
        ext = item.image.rsplit('.', 1)[-1].lower() if '.' in item.image else ''
        mime_type = MIME_MAP.get(ext, 'image/jpeg')

        enclosure = Enclosure(image_url, '0', mime_type)
        feed.items[-1]['enclosures'] = [enclosure]


def register():
    """Called by Pelican to activate the plugin."""
    Writer._add_item_to_the_feed = _add_item_with_image
