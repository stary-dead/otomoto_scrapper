from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from articles import Article
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os
from dotenv import load_dotenv

load_dotenv()

class Scrapper(ABC):
    def __init__(self):
        os.getenv("DRIVER_PATH")
        self.driver_path = os.getenv("DRIVER_PATH")
        self.driver: webdriver.Firefox | None = None 
        self.setup_driver()

    def setup_driver(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--disable-blink-features=AutomationControlled")
        firefox_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Создаем профиль Firefox и указываем путь к нему
        profile_path = "C:/Users/stary/AppData/Local/Mozilla/Firefox/Profiles/eii072yg.default-release"
        firefox_profile = FirefoxProfile(profile_path)

        # Подключаем профиль к опциям браузера
        firefox_options.profile = firefox_profile

        self.driver = webdriver.Firefox(service=Service(self.driver_path), options=firefox_options)

    def close(self):
        """Закрытие драйвера."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    @abstractmethod
    def get_articles(self, brand_id, model_id=None):
        """Абстрактный метод для получения статей."""
        pass

    @property
    @abstractmethod
    def brands(self)->dict:
        """Абстрактное свойство для списка брендов."""
        pass
