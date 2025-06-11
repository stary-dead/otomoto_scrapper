import requests
from bs4 import BeautifulSoup
from articles import KleinzengenArticle
from dotenv import load_dotenv
from .base import Scrapper  # Импортируем базовый класс
from utils.brand import Brand, BrandsSerializer
from filters import KleinzengenFilter
import time
import random
import logging  # Добавляем импорт модуля логирования

load_dotenv()

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Если обработчики ещё не настроены, создаем и добавляем их
if not logger.handlers:
    # Создаем обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчик к логгеру
    logger.addHandler(console_handler)

class KleinzengenRequestsScrapper(Scrapper):
    """
    Скраппер для kleinanzeigen.de, использующий прямые HTTP-запросы вместо Selenium.
    """
    # Список user-agents для ротации
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    def __init__(self):
        logger.info("Инициализация KleinzengenRequestsScrapper")
        try:
            with open('kleinzengen_brands.json', 'r', encoding='utf-8') as file:
                self._brands = BrandsSerializer.deserialize(file.read())
                logger.info("Бренды успешно загружены из файла")
              # Инициализируем сессию requests
            self.session = requests.Session()
            # Установка таймаутов для сессии
            self.timeout = (10, 30)  # (connect timeout, read timeout)
            # Установка базовых заголовков для всех запросов
            self.update_headers()
            logger.debug("Сессия requests инициализирована с таймаутами")
            
            # Явно указываем, что мы не используем Selenium
            super().__init__
        except Exception as e:
            logger.error(f"Ошибка при инициализации скраппера: {e}")
            raise
    
    def __str__(self) -> str:
        return "Kleinzengen"
    
    def update_headers(self):
        """Обновляет заголовки запроса с случайным user-agent"""
        try:
            user_agent = random.choice(self.USER_AGENTS)
            self.session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.kleinanzeigen.de/',
                'DNT': '1',  # Do Not Track
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Cache-Control': 'max-age=0',
            })
            logger.debug(f"Заголовки обновлены с User-Agent: {user_agent[:30]}...")
        except Exception as e:
            logger.error(f"Ошибка при обновлении заголовков: {e}")

    def get_articles(self, user_filter: KleinzengenFilter, page=1) -> list[KleinzengenArticle]:
        """
        Получает статьи с сайта kleinanzeigen.de на основе указанных фильтров.
        
        Args:
            user_filter: Объект фильтра с параметрами поиска
            page: Номер страницы для получения
            
        Returns:
            Список объектов KleinzengenArticle
        """
        user_filter._page = page
        try:
            url = user_filter.get_web_url()  # Добавляем скобки для вызова метода
            logger.info(f"Получение статей со страницы {page}, URL: {url}")
            
            # Обновляем заголовки перед запросом для имитации нового сеанса
            self.update_headers()
            
            # Добавляем небольшую задержку для имитации человеческого поведения
            delay = random.uniform(1, 3)
            logger.debug(f"Задержка перед запросом: {delay:.2f} сек")
            time.sleep(delay)
              # Выполняем запрос
            logger.debug(f"Выполнение GET-запроса к {url}")
            try:
                response = self.session.get(url, timeout=self.timeout)
                logger.info(f"Статус ответа: {response.status_code}")
                logger.debug(f"Заголовки ответа: {dict(response.headers)}")
                
                response.raise_for_status()  # Проверка на ошибки HTTP
                
                # Логируем информацию о содержимом
                content_length = len(response.text)
                logger.info(f"Получен ответ, размер содержимого: {content_length} символов")
                
                # Логируем начало содержимого для диагностики
                preview = response.text[:500] if response.text else "Пустой ответ"
                logger.debug(f"Превью содержимого: {preview}...")
                
            except requests.exceptions.Timeout:
                logger.error(f"Таймаут при запросе к {url}")
                return []
            except requests.exceptions.ConnectionError:
                logger.error(f"Ошибка соединения при запросе к {url}")
                return []
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP ошибка {response.status_code} при запросе к {url}: {e}")
                # Логируем содержимое ошибки если оно есть
                if hasattr(e, 'response') and e.response:
                    error_content = e.response.text[:1000] if e.response.text else "Нет содержимого"
                    logger.debug(f"Содержимое ошибки: {error_content}")
                return []
            except requests.exceptions.RequestException as e:
                logger.error(f"Общая ошибка запроса к {url}: {e}")
                return []              # Используем BeautifulSoup для парсинга
            soup = BeautifulSoup(response.text, 'html.parser')            
            articles = soup.select('li.ad-listitem')
            
            logger.info(f"Найдено {len(articles)} элементов статей на странице")
            
            # Если не удалось найти элементы, возможно, нас заблокировали
            if not articles:
                logger.warning("Не удалось найти элементы. Возможно, запрос был заблокирован.")
                # Логируем структуру страницы для диагностики
                page_title = soup.find('title')
                title_text = page_title.text if page_title else "Заголовок не найден"
                logger.debug(f"Заголовок страницы: {title_text}")
                
                # Проверяем на наличие капчи или других блокировок
                if "captcha" in response.text.lower() or "blocked" in response.text.lower():
                    logger.warning("Обнаружена возможная капча или блокировка")
                
                return []  # Возвращаем пустой список вместо None
                  # Парсим статьи
            result = []
            logger.debug("Начинаем парсинг найденных статей")
            for i, article_html in enumerate(articles, 1):
                try:
                    logger.debug(f"Парсинг статьи {i}/{len(articles)}")
                    article = self._parse_article(article_html)
                    if article:
                        result.append(article)
                        logger.debug(f"Статья {i} успешно обработана: {article.title[:50]}...")
                    else:
                        logger.debug(f"Статья {i} пропущена (реклама или ошибка парсинга)")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге статьи {i}: {e}")
            
            logger.info(f"Успешно обработано {len(result)} из {len(articles)} статей")
            return result
        except Exception as e:
            logger.error(f"Произошла ошибка при выполнении запроса: {e}")
            return []  # Возвращаем пустой список вместо None
            
    def _parse_article(self, article):
        """
        Парсит HTML элемент статьи и возвращает объект KleinzengenArticle
        
        Args:
            article: BS4 элемент, представляющий статью
            
        Returns:
            KleinzengenArticle объект или None если статью не удалось распарсить
        """
        try:
            # Проверяем, что это не рекламная статья
            exclude_classes = {"is-highlight", "badge-topad", "is-topad"}
            article_classes = set(article.get('class', []))
            if article_classes & exclude_classes:  # Проверяет пересечение классов
                logger.debug("Пропускаем рекламное объявление")
                return None
                
            # Заголовок
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
            if image_element and image_element.has_attr('src'):
                image_url = image_element['src']
            else:
                image_url = "https://sesupport.edumall.jp/hc/article_attachments/900009570963/noImage.jpg"
                
            # URL объявления
            article_tag = article.select_one('article')
            if article_tag and article_tag.has_attr('data-href'):
                data_href = article_tag.get('data-href', 'No href')
                article_url = f"https://www.kleinanzeigen.de{data_href}" if data_href != 'No href' else None
            else:
                article_url = None
                
            # Пропускаем объявления без URL
            if not article_url:
                logger.debug("Пропускаем объявление без URL")
                return None
                
            # Создаем и возвращаем объект статьи
            item = KleinzengenArticle(
                title=title, 
                price=price, 
                main_image=image_url, 
                mileage=mileage, 
                description=f"{year}\n{description}", 
                url=article_url
            )
            
            return item
            
        except Exception as e:
            logger.error(f"Ошибка при разборе элемента статьи: {str(e)}")
            return None
            
    def close(self):
        """Закрывает сессию запросов"""
        logger.info("Закрытие сессии KleinzengenRequestsScrapper")
        if self.session:
            self.session.close()
            logger.debug("Сессия requests закрыта")
        # Также вызываем метод базового класса для совместимости
        super().close()
    
    @property
    def brands(self) -> dict[str, Brand]:
        return self._brands
