from pelican import signals
from collections import defaultdict

def related_posts(generator):
    """
    Finds related posts for each article based on shared tags.
    """
    # Group articles by tag
    tag_map = defaultdict(list)
    for article in generator.articles:
        if hasattr(article, 'tags'):
            for tag in article.tags:
                tag_map[tag].append(article)

    # Find related posts for each article
    for article in generator.articles:
        related = set()
        if hasattr(article, 'tags'):
            for tag in article.tags:
                for other_article in tag_map[tag]:
                    if other_article != article:
                        related.add(other_article)
        
        # Sort by date (newest first) and take top 5
        article.related_posts = sorted(list(related), key=lambda x: x.date, reverse=True)[:5]

def register():
    signals.article_generator_finalized.connect(related_posts)
