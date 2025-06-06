import pytest
from tests.mocks.kleinzengen_article_mock import KleinzengenArticle
from tests.mocks.kleinzengen_filter_mock import KleinzengenFilter
from tests.mocks.kleinzengen_scrapper_mock import KleinzengenScrapper
from tests.mocks.subscriptions_handler_mock import SubscriptionsHandler

@pytest.fixture
def kleinzengen_scrapper():
    return KleinzengenScrapper()

@pytest.fixture
def kleinzengen_filter():
    return KleinzengenFilter()

@pytest.fixture
def sample_article_data():
    return {
        "title": "Test Car",
        "price": "10000",
        "year": "2020",
        "mileage": "50000",
        "url": "http://example.com/car",
        "brand": "BMW"
    }

@pytest.fixture
def kleinzengen_article(sample_article_data):
    return KleinzengenArticle(**sample_article_data)
