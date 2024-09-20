from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from articles import OtomotoArticle
import time, os
from dotenv import load_dotenv
from .base import Scrapper
from utils.brand import Brand
load_dotenv()
class OtomotoScrapper(Scrapper):
    def __init__(self):
        self._brands = {
    "BMW": Brand("BMW", 'bmw', {
        '1M': '1m', '3GT': '3gt', '5GT': '5gt', '6GT': '6gt', 'i3': 'i3',
        'i4': 'i4', 'i5': 'i5', 'i7': 'i7', 'i8': 'i8', 'Inny': 'ix',
        'iX': 'ix1', 'iX1': 'ix2', 'iX2': 'ix3', 'iX3': 'm2', 'M2': 'm3',
        'M3': 'm4', 'M4': 'm5', 'M5': 'm6', 'M6': 'm8', 'M8': 'other',
        'Seria 1': 'seria-1', 'Seria 2': 'seria-2', 'Seria 3': 'seria-3',
        'Seria 4': 'seria-4', 'Seria 5': 'seria-5', 'Seria 6': 'seria-6',
        'Seria 7': 'seria-7', 'Seria 8': 'seria-8', 'X1': 'x1', 'X2': 'x2',
        'X3': 'x3', 'X3 M': 'x3-m', 'X4': 'x4', 'X4 M': 'x4-m', 'X5': 'x5',
        'X5 M': 'x5-m', 'X6': 'x6', 'X6M': 'x6-m', 'X7': 'x7', 'XM': 'xm',
        'Z1': 'z1', 'Z3': 'z3', 'Z4': 'z4', 'Z4 M': 'z4-m', 'Z8': 'z8'
    }),
    "Audi": Brand("Audi", 'audi', {
        'A1': 'a1', 'A3': 'a3', 'A4': 'a4', 'A5': 'a5', 'A6': 'a6', 'A7': 'a7',
        'A8': 'a8', 'Q2': 'q2', 'Q3': 'q3', 'Q5': 'q5', 'Q7': 'q7', 'Q8': 'q8',
        'TT': 'tt', 'R8': 'r8', 'e-tron': 'etron'
    })

}
        super().__init__()

    def get_articles(self, brand_id, model_id=None) -> list[OtomotoArticle]:
        if not model_id:
            model_id = ""
        url = f"https://www.otomoto.pl/osobowe/{brand_id}/{model_id}?search%5Border%5D=created_at_first%3Adesc"

        if not self.driver:
            self.setup_driver()

        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ooa-r53y0q.eupw8r111'))
        )
        articles_container = self.driver.find_element(By.CLASS_NAME, 'ooa-r53y0q.eupw8r111')
        titles = []
        articles = articles_container.find_elements(By.CSS_SELECTOR, 'article.ooa-yca59n.efpuxbr0')
        for child in articles:
            price_list = child.find_elements(By.CLASS_NAME, "ooa-2p9dfw.efpuxbr4")
            title_list = child.find_elements(By.TAG_NAME, 'h1')
            image_list = child.find_elements(By.TAG_NAME, 'img')
            subtitle_list = child.find_elements(By.TAG_NAME, 'p')
            if title_list and image_list and subtitle_list and price_list:
                title=title_list[0].text.strip()
                price = price_list[0].text.strip().replace('\n', '')
                image_url = image_list[0].get_attribute("src")
                description = subtitle_list[0].text.strip()
                article = OtomotoArticle(title=title, price=price, main_image=image_url, description=description)
                titles.append(article)

        return titles
    def scrape_page(self, url):
        if not self.driver:
            self.setup_driver()

        self.driver.get(url)
        time.sleep(3)

        articles_container = self.driver.find_element(By.CLASS_NAME, 'ooa-r53y0q.eupw8r111')
        titles = []
        articles = articles_container.find_elements(By.TAG_NAME, 'div')
        for child in articles:
            title_list = child.find_elements(By.TAG_NAME, 'h1')
            if title_list:
                titles.append(title_list[0].text)

        return titles

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    @property
    def brands(self)->dict[str, Brand]:
        return self._brands

if __name__ == "__main__":
    chrome_driver_path = os.getenv("DRIVER_PATH")
    scrapper = Scrapper(chrome_driver_path)
    titles = scrapper.scrape_page("https://www.otomoto.pl/osobowe/bmw")
    
    print(titles)
    scrapper.close()
