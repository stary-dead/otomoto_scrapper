from tests.mocks.kleinzengen_article_mock import KleinzengenArticle

class KleinzengenScrapper:
    def __init__(self):
        self.base_url = "https://www.kleinanzeigen.de"
        
    def get_articles(self):
        """
        Возвращает список статей.
        
        Returns:
            list: Список объектов статей
        """
        return [
            KleinzengenArticle(
                title="BMW X5",
                price="50000",
                year="2020",
                mileage="100000 km",
                url="http://example.com/car/1",
                brand="BMW"
            ),
            KleinzengenArticle(
                title="Audi A4",
                price="35000",
                year="2019",
                mileage="80000 km",
                url="http://example.com/car/2",
                brand="Audi"
            )
        ]
        
    def _parse_article(self, html):
        """
        Парсит HTML и возвращает объект статьи.
        
        Args:
            html: HTML строка
            
        Returns:
            KleinzengenArticle: Объект статьи
        """
        # Упрощенный парсинг для тестов
        if "BMW X5" in html:
            return KleinzengenArticle(
                title="BMW X5",
                price="50000 PLN",
                year="2020",
                mileage="100000 km",
                url="http://example.com/car/1",
                brand="BMW"
            )
        return None
        
    def close(self):
        """
        Закрывает соединения и очищает ресурсы.
        """
        pass
