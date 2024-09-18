from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time

chrome_driver_path = 'C:/Users/stary/.wdm/drivers/chromedriver/win64/128.0.6613.137/chromedriver-win32/chromedriver.exe'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
import time
driver.get("https://www.otomoto.pl/osobowe/bmw")
time.sleep(3)
with open("text.txt", 'w', encoding='utf-8') as file:
    file.write(driver.page_source)
articles_container = driver.find_element(By.CLASS_NAME, 'ooa-r53y0q.eupw8r111')
titles = []
articles = articles_container.find_elements(By.TAG_NAME, 'div')
for child in articles:
    title_list = child.find_elements(By.TAG_NAME, 'h1')
    if title_list:
        titles.append(title_list[0].text)

print(len(titles))
driver.quit()
