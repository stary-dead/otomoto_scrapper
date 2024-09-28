from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from articles import KleinzengenArticle
from dotenv import load_dotenv
from .base import Scrapper
from utils.brand import Brand, BrandsSerializer
from bs4 import BeautifulSoup
load_dotenv()

class KleinzengenScrapper(Scrapper):
    def __init__(self):

        with open('kleinzengen_brands.json', 'r', encoding='utf-8') as file:
            self._brands = BrandsSerializer.deserialize(file.read())
        
        super().__init__()
    def __str__(self) -> str:
        return "Kleinzengen"

    def get_articles(self, brand_id, model_id=None, page = 1) -> list[KleinzengenArticle]:
        url = f"https://www.kleinanzeigen.de/s-autos/{brand_id}/seite:{page}/c216+autos.marke_s:{brand_id}"
        if model_id:
            url += "+autos.model_s:" + model_id

        print(url)
        self.driver.get(url)
        
        # Ожидание полной загрузки страницы
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article.aditem'))
        )
        
        # Получаем HTML страницы
        page_source = self.driver.page_source
        
        # Используем BeautifulSoup для парсинга
        soup = BeautifulSoup(page_source, 'html.parser')
        articles = soup.select('li.ad-listitem')
        exclude_classes = {"is-highlight", "badge-topad","is-topad"}
        results = []
        
        for article in articles: 
            article_classes = set(article.get('class', []))
            if article_classes & exclude_classes:  # Проверяет пересечение классов
                continue 
            title_element = article.select_one('h2.text-module-begin > a.ellipsis')
            title = title_element.text.strip() if title_element else "No title"
            
            # Описание
            description_element = article.select_one('p.aditem-main--middle--description')
            description = description_element.text.strip() if description_element else "No description"
            
            # Цена
            price_element = article.select_one('p.aditem-main--middle--price-shipping--price')
            price = price_element.text.strip() if price_element else "No price"
            
            # Пробег и год
            tags = article.select('span.simpletag')
            mileage = tags[0].text.strip() if len(tags) > 0 else "No mileage"
            year = tags[1].text.strip() if len(tags) > 1 else "No year"
            
            # Ссылка на изображение
            image_element = article.select_one('div.aditem-image img')
            image_url = image_element['src'] if image_element else "No image"
            
            item = KleinzengenArticle(title=title, price=price, main_image=image_url, mileage=mileage, description=f"{year}\n{description}")
            results.append(item)

        
        return results

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    @property
    def brands(self)->dict[str, Brand]:
        return self._brands

if __name__ == "__main__":
    scrapper = KleinzengenScrapper()
    titles = scrapper.get_articles()
    
    scrapper.close()
