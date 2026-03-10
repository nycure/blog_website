
import os
import logging
from urllib.parse import urljoin, urlparse

from pelican.writers import Writer
try:
    from pelican.feedgenerator import Atom1Feed, Rss201rev2Feed
except ImportError:
    try:
        from feedgenerator import Atom1Feed, Rss201rev2Feed
    except ImportError:
        # Fallback to simple import if specific classes aren't found directly
        import feedgenerator
        Atom1Feed = feedgenerator.Atom1Feed
        Rss201rev2Feed = feedgenerator.Rss201rev2Feed

logger = logging.getLogger(__name__)

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

class MediaAwareAtomFeed(Atom1Feed):
    """
    Atom Feed generator that includes Media RSS namespace and elements.
    """
    def root_attributes(self):
        attrs = super(MediaAwareAtomFeed, self).root_attributes()
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs

    def add_item_elements(self, handler, item):
        super(MediaAwareAtomFeed, self).add_item_elements(handler, item)
        
        if 'media_content' in item:
            media = item['media_content']
            # Convert integer size/width/height to string if present
            attrs = {
                'url': media['url'],
                'type': media['type'],
                'medium': 'image'
            }
            
            # fileSize: Omit if 0 or unknown
            if media.get('fileSize') and int(media['fileSize']) > 0:
                attrs['fileSize'] = str(media['fileSize'])
                
            # width/height: Include if available
            if media.get('width'):
                attrs['width'] = str(media['width'])
            if media.get('height'):
                attrs['height'] = str(media['height'])
                
            handler.addQuickElement('media:content', '', attrs)
            
            # Add media:title and media:description if available
            if media.get('title'):
                handler.addQuickElement('media:title', media['title'], {'type': 'plain'})
            if media.get('description'):
                handler.addQuickElement('media:description', media['description'], {'type': 'plain'})


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

        # Try to get file info (size, dimensions) if it's a local file
        file_size = 0
        width = 1200 # Default/Fallback width
        height = 675 # Default/Fallback height
        
        # We can implement local file check here if needed, 
        # but for now we'll stick to safe defaults/0 for size to avoid build perf hit
        # unless user strictly wants local lookup.
        # Given the "don't output 0" rule, we default size to 0 and logic handles omission.

        # Prepare dictionary for MediaAwareAtomFeed
        
        # Helper to strip HTML tags
        def strip_html(text):
            if not text: return ''
            import re
            # Remove HTML tags
            clean = re.sub('<[^<]+?>', '', str(text))
            # Unescape HTML entities (optional but good for "plain" text)
            import html
            return html.unescape(clean).strip()

        media_data = {
            'url': image_url,
            'type': mime_type,
            'fileSize': file_size, # Will be omitted by feed class logic since it's 0
            'width': width,
            'height': height,
            'title': strip_html(getattr(item, 'title', '')),
            'description': strip_html(getattr(item, 'summary', ''))
        }
        
        # Feed-specific injection
        current_item = feed.items[-1]
        
        # 1. For Atom feeds (using our new class implies checking if it supports media_content)
        # However, Pelican generates the feed object. We need to populate 'media_content' in the item dict
        # which our custom feed class will read.
        current_item['media_content'] = media_data

        # 2. RSS Fallback (keep standard enclosure for RSS)
        # RSS doesn't use the custom MediaAwareAtomFeed class usually (unless we swap that too),
        # so we keep the standard enclosure logic for RSS feeds.
        if 'Rss' in feed.__class__.__name__:
             from feedgenerator import Enclosure
             # For RSS, we can default length to "0" if unknown, or try to find it.
             # Standard RSS enclosures usually require a length attribute.
             enclosure = Enclosure(image_url, '0', mime_type)
             existing = current_item.get('enclosures', [])
             if existing is None: existing = []
             elif isinstance(existing, tuple): existing = list(existing)
             existing.append(enclosure)
             current_item['enclosures'] = existing

def register():
    """Called by Pelican to activate the plugin."""
    # Monkeypatch the add_item method
    Writer._add_item_to_the_feed = _add_item_with_image
    
    # Crucial: Monkeypatch the Atom feed class used by Pelican
    # This enforces usage of our MediaAwareAtomFeed instead of the default Atom1Feed
    import pelican.writers
    pelican.writers.Atom1Feed = MediaAwareAtomFeed

