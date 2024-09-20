from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from articles import Article
import os
from dotenv import load_dotenv

load_dotenv()

class Scrapper(ABC):
    def __init__(self):
        os.getenv("DRIVER_PATH")
        self.driver_path = os.getenv("DRIVER_PATH")
        self.driver: webdriver.Chrome | None = None 
        self.setup_driver()

    def setup_driver(self):
        """Настройка WebDriver с необходимыми опциями."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)

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
