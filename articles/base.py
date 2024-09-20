from abc import ABC, abstractmethod
from typing import List

class Article(ABC):
    @property
    @abstractmethod
    def title(self) -> str:
        """Заголовок артикула"""
        pass

    @property
    @abstractmethod
    def price(self) -> float:
        """Цена артикула"""
        pass

    @property
    @abstractmethod
    def city(self) -> str:
        """Город, где находится артикул"""
        pass

    @property
    @abstractmethod
    def mileage(self) -> int:
        """Пробег артикула"""
        pass

    @property
    @abstractmethod
    def main_image(self) -> str:
        """URL главной картинки"""
        pass

    @property
    @abstractmethod
    def image_list(self) -> List[str]:
        """Список URL других картинок"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Описание артикула"""
        pass