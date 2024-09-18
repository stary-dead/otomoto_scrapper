from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
from dotenv import load_dotenv
load_dotenv()
class Scrapper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)

    def get_articles(self, brand_id, model_id=""):
        url = f"https://www.otomoto.pl/osobowe/{brand_id}/{model_id}"

        if not self.driver:
            self.setup_driver()

        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ooa-r53y0q.eupw8r111'))
        )
        articles_container = self.driver.find_element(By.CLASS_NAME, 'ooa-r53y0q.eupw8r111')
        titles = []
        articles = articles_container.find_elements(By.TAG_NAME, 'article')
        for child in articles:
            price_list = child.find_elements(By.CLASS_NAME, "ooa-2p9dfw.efpuxbr4")
            title_list = child.find_elements(By.TAG_NAME, 'h1')
            image_list = child.find_elements(By.TAG_NAME, 'img')
            subtitle_list = child.find_elements(By.TAG_NAME, 'p')
            if title_list and image_list and subtitle_list and price_list:
                titles.append({"title":title_list[0].text, "image":image_list[0].get_attribute("src"), 'sub_title':subtitle_list[0].text, 'price':price_list[0].text})

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


if __name__ == "__main__":
    chrome_driver_path = os.getenv("DRIVER_PATH")
    scrapper = Scrapper(chrome_driver_path)
    titles = scrapper.scrape_page("https://www.otomoto.pl/osobowe/bmw")
    
    print(titles)
    scrapper.close()
