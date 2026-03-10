
import sys
from feedgenerator import Rss201rev2Feed, Enclosure

def test_rss_enclosure():
    feed = Rss201rev2Feed(
        title="Test Feed",
        link="http://example.com",
        description="Test"
    )
    
    feed.add_item(
        title="Test Item",
        link="http://example.com/item",
        description="Test Description"
    )
    
    # Simulate the plugin logic
    current_item = feed.items[-1]
    if 'enclosures' not in current_item:
        current_item['enclosures'] = []
    
    enclosure = Enclosure("http://example.com/image.jpg", "0", "image/jpeg")
    current_item['enclosures'].append(enclosure)
    
    print(f"Item enclosures: {current_item['enclosures']}")
    
    # Write to stdout
    feed.write(sys.stdout, 'utf-8')

if __name__ == "__main__":
    test_rss_enclosure()
