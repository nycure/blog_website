from pelican import signals
from collections import defaultdict

def related_posts(generator):
    """
    Finds related posts for each article based on shared tags.
    Posts are scored by the number of shared tags (higher = more related).
    Only posts sharing at least 2 tags are shown, top 3 results.
    """
    # Group articles by tag
    tag_map = defaultdict(list)
    for article in generator.articles:
        if hasattr(article, 'tags'):
            for tag in article.tags:
                tag_map[tag].append(article)

    # Score each candidate by number of shared tags
    for article in generator.articles:
        scores = {}
        if hasattr(article, 'tags'):
            for tag in article.tags:
                for other in tag_map[tag]:
                    if other != article:
                        scores[other] = scores.get(other, 0) + 1

        # Filter: require at least 2 shared tags, then sort by score desc, take top 3
        qualified = {a: s for a, s in scores.items() if s >= 2}
        article.related_posts = sorted(
            qualified.keys(),
            key=lambda a: qualified[a],
            reverse=True
        )[:3]

def register():
    signals.article_generator_finalized.connect(related_posts)
