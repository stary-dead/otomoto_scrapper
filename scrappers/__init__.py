from .base import Scrapper
from .kleinzengen_scrapper import KleinzengenScrapperMock
from .kleinzengen_requests_scrapper import KleinzengenRequestsScrapper

# Используем RequestsScrapper вместо старых скрапперов с Selenium
# Оставляем алиасы для обратной совместимости с существующим кодом
KleinzengenScrapper = KleinzengenRequestsScrapper
# OtomotoScrapper = OtomotoRequestsScrapper

__all__ = ['Scrapper', 'KleinzengenScrapperMock', 'KleinzengenRequestsScrapper']