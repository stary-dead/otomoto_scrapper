import pytest
from tests.mocks.kleinzengen_filter_mock import KleinzengenFilter

def test_filter_initialization(kleinzengen_filter):
    assert isinstance(kleinzengen_filter, KleinzengenFilter)

def test_filter_apply(kleinzengen_filter, kleinzengen_article):
    # Тест базовой фильтрации
    kleinzengen_filter.min_price = 5000
    kleinzengen_filter.max_price = 15000
    assert kleinzengen_filter.apply(kleinzengen_article) is True

    # Тест фильтрации по цене выше максимальной
    kleinzengen_filter.max_price = 9000
    assert kleinzengen_filter.apply(kleinzengen_article) is False

def test_filter_brand_matching(kleinzengen_filter, kleinzengen_article):
    # Тест фильтрации по бренду
    kleinzengen_filter.brands = ["BMW"]
    assert kleinzengen_filter.apply(kleinzengen_article) is True
    
    kleinzengen_filter.brands = ["Audi"]
    assert kleinzengen_filter.apply(kleinzengen_article) is False

def test_filter_year_range(kleinzengen_filter, kleinzengen_article):
    # Тест фильтрации по году
    kleinzengen_filter.min_year = 2019
    kleinzengen_filter.max_year = 2021
    assert kleinzengen_filter.apply(kleinzengen_article) is True
    
    kleinzengen_filter.min_year = 2021
    assert kleinzengen_filter.apply(kleinzengen_article) is False
