from tests.mocks.base_article_mock import Article

class KleinzengenArticle(Article):
    def __init__(self, title, price, year=None, mileage=None, url=None, brand=None, 
                 main_image=None, description=None, city=None, image_list=None):
        self._title = title
        self._price = price
        self._year = year
        self._mileage = mileage
        self._url = url
        self._brand = brand
        self._main_image = main_image or "http://example.com/image.jpg"
        self._description = description or "No description"
        self._city = city or "Berlin"
        self._image_list = image_list or []
        
    def __str__(self) -> str:
        return f"{self.title} - {self.price}"
    
    def __eq__(self, other):
        if not isinstance(other, KleinzengenArticle):
            return False
        return (self.title == other.title and
                self.price == other.price and
                self.url == other.url and
                self.year == other.year and
                self.mileage == other.mileage and
                self.brand == other.brand)
    
    @property
    def title(self):
        return self._title
        
    @property
    def price(self):
        return self._price
        
    @property
    def year(self):
        return self._year
        
    @property
    def mileage(self):
        return self._mileage
        
    @property
    def url(self):
        return self._url
        
    @property
    def brand(self):
        return self._brand
        
    @property
    def main_image(self):
        return self._main_image
        
    @property
    def description(self):
        return self._description
        
    @property
    def city(self):
        return self._city
        
    @property
    def image_list(self):
        return self._image_list
