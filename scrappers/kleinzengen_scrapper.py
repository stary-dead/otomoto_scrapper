from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from articles import KleinzengenArticle
from dotenv import load_dotenv
from .base import Scrapper
from utils.brand import Brand, BrandsSerializer
from bs4 import BeautifulSoup
from filters import KleinzengenFilter

load_dotenv()

class KleinzengenScrapper(Scrapper):
    def __init__(self):
        with open('kleinzengen_brands.json', 'r', encoding='utf-8') as file:
            self._brands = BrandsSerializer.deserialize(file.read())
        
        # Явно указываем, что хотим использовать Selenium
        super().__init__(use_selenium=True)
    def __str__(self) -> str:
        return "Kleinzengen"

    def get_articles(self, user_filter:KleinzengenFilter, page=1) -> list[KleinzengenArticle]:
        user_filter._page = page
        url = user_filter.get_web_url


        # print(url)
        self.driver.get(url)
        
        # Ожидание полной загрузки страницы
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.ad-listitem'))
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
            if image_element:
                image_url = image_element['src']
            else:
                image_url = "https://sesupport.edumall.jp/hc/article_attachments/900009570963/noImage.jpg"
            article_tag = article.select_one('article')
            if article_tag:
                data_href = article_tag.get('data-href', 'No href')
                article_url = f"https://www.kleinanzeigen.de{data_href}" if data_href != 'No href' else None
            else:
                article_url = None
            if not article_url:
                continue
             
            item = KleinzengenArticle(title=title, price=price, main_image=image_url, mileage=mileage, description=f"{year}\n{description}", url=article_url)
            results.append(item)

        
        return results

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    @property
    def brands(self)->dict[str, Brand]:
        return self._brands
    
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from .base import Scrapper
from utils.brand import Brand, BrandsSerializer
from articles import KleinzengenArticle
import random

load_dotenv()

class KleinzengenScrapperMock(Scrapper):
    def __init__(self):
        with open('kleinzengen_brands.json', 'r', encoding='utf-8') as file:
            self._brands = BrandsSerializer.deserialize(file.read())
        
        # Не используем Selenium в моке
        super().__init__(use_selenium=False)

    def __str__(self) -> str:
        return "Kleinzengen"

    def get_articles(self, user_filter:KleinzengenFilter, page=1) -> list[KleinzengenArticle]:
        # Возвращаем моковые данные
        mock_articles = []
        # url = await user_filter.get_web_url(page=page)
        # print(url)
        for i in range(10):  # Генерируем 10 моковых статей
            mock_articles.append(
                KleinzengenArticle(
                    title=f"Mock Car {user_filter.brand} {i}",
                    price=f"{random.randint(5000, 50000)} €",
                    main_image="https://sesupport.edumall.jp/hc/article_attachments/900009570963/noImage.jpg",
                    mileage=f"{random.randint(10000, 200000)} km",
                    description=f"Year: {2020 - random.randint(0, 10)}\nMock description for car {i}",
                    url= user_filter.get_web_url
                )
            )
        return mock_articles

    def close(self):
        # Метод оставляем, чтобы соответствовать интерфейсу, но ничего не делаем
        pass

    @property
    def brands(self) -> dict[str, Brand]:
        return self._brands

# if __name__ == "__main__":
#     scrapper = KleinzengenScrapper()
#     articles = scrapper.get_articles(brand_id="mock_brand", model_id="mock_model", page=1)
#     for article in articles:
#         print(article)
#     scrapper.close()


# if __name__ == "__main__":
#     scrapper = KleinzengenScrapper()
#     titles = scrapper.get_articles()
    
#     scrapper.close()
