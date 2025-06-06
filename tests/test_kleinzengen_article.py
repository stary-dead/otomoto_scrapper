import pytest
from tests.mocks.kleinzengen_article_mock import KleinzengenArticle

def test_article_creation(sample_article_data):
    article = KleinzengenArticle(**sample_article_data)
    assert article.title == sample_article_data["title"]
    assert article.price == sample_article_data["price"]
    assert article.year == sample_article_data["year"]
    assert article.mileage == sample_article_data["mileage"]
    assert article.url == sample_article_data["url"]
    assert article.brand == sample_article_data["brand"]

def test_article_str_representation(kleinzengen_article):
    article_str = str(kleinzengen_article)
    assert kleinzengen_article.title in article_str
    assert kleinzengen_article.price in article_str

def test_article_equality(sample_article_data):
    article1 = KleinzengenArticle(**sample_article_data)
    article2 = KleinzengenArticle(**sample_article_data)
    assert article1 == article2
    
    # Test inequality
    modified_data = sample_article_data.copy()
    modified_data["price"] = "20000"
    article3 = KleinzengenArticle(**modified_data)
    assert article1 != article3
