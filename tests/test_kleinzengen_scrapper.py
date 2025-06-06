import pytest
from tests.mocks.kleinzengen_scrapper_mock import KleinzengenScrapper

def test_scrapper_initialization(kleinzengen_scrapper):
    assert isinstance(kleinzengen_scrapper, KleinzengenScrapper)
    assert kleinzengen_scrapper.base_url is not None

def test_scrapper_get_articles(kleinzengen_scrapper):
    articles = kleinzengen_scrapper.get_articles()
    assert isinstance(articles, list)
    if len(articles) > 0:
        article = articles[0]
        assert hasattr(article, 'title')
        assert hasattr(article, 'price')
        assert hasattr(article, 'url')

def test_scrapper_parse_article(kleinzengen_scrapper):
    # Тест с моковыми данными HTML
    sample_html = """
    <div class="offer-item">
        <h2 class="offer-title">BMW X5</h2>
        <span class="price">50000 PLN</span>
        <div class="params">2020</div>
        <div class="mileage">100000 km</div>
    </div>
    """
    article = kleinzengen_scrapper._parse_article(sample_html)
    assert article is not None
    assert article.title == "BMW X5"
