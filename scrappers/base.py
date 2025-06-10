from abc import ABC, abstractmethod
from articles import Article
import os
from dotenv import load_dotenv

load_dotenv()

class Scrapper(ABC):
    def __init__(self):
        """
        Инициализация базового класса скраппера.
        """
        pass
        
    def close(self):
        """
        Метод для освобождения ресурсов.
        Подклассы могут переопределить этот метод для выполнения специфических действий.
        """
        pass

    @abstractmethod
    def get_articles(self, *args, **kwargs):
        """
        Абстрактный метод для получения статей.
        Должен быть реализован в подклассах.
        """
        pass

    @property
    @abstractmethod
    def brands(self)->dict:
        """
        Абстрактное свойство для списка брендов.
        Должно быть реализовано в подклассах.
        """
        pass
