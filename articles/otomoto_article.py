from .base import Article

class OtomotoArticle(Article):
    def __init__(self, title: str, price: str,  main_image: str, mileage: str | None = None, city: str | None = None, image_list: list[str] | None = None, description: str | None = None):
        self._title = title
        self._price = price
        self._city = city
        self._mileage = mileage
        self._main_image = main_image
        self._image_list = image_list
        self._description = description

    @property
    def title(self) -> str:
        return self._title

    @property
    def price(self) -> str:
        return self._price

    @property
    def city(self) -> str:
        return self._city

    @property
    def mileage(self) -> str:
        return self._mileage

    @property
    def main_image(self) -> str:
        return self._main_image

    @property
    def image_list(self) -> list[str]:
        return self._image_list

    @property
    def description(self) -> str:
        return self._description