from scrappers.kleinzengen_requests_scrapper import KleinzengenRequestsScrapper
from filters import KleinzengenFilter

def main():
    # Создаем экземпляр скраппера с использованием requests вместо Selenium
    scrapper = KleinzengenRequestsScrapper()
    
    print("Тестирование скраппера с requests...")
    
    # Создаем простой фильтр для тестирования
    test_filter = KleinzengenFilter(
        brand={"brand_id": "audi", "model_id": "all"},  # Можно изменить на любую другую марку
        page=1
    )
    
    try:
        # Получаем статьи с помощью нового скраппера
        articles = scrapper.get_articles(test_filter)
        
        # Выводим результат
        print(f"Найдено объявлений: {len(articles)}")
        for i, article in enumerate(articles, 1):            print(f"\nОбъявление {i}:")
            print(f"Название: {article.title}")
            print(f"Цена: {article.price}")
            print(f"Пробег: {article.mileage}")
            print(f"Описание: {article.description[:50]}...")  # Выводим только часть описания
            print(f"URL: {article.url}")
            print(f"Изображение: {article.main_image}")
            print("-" * 50)
        
    except Exception as e:
        print(f"Произошла ошибка при тестировании: {e}")
    
    finally:
        # Закрываем сессию
        scrapper.close()
        print("Тестирование завершено.")

if __name__ == "__main__":
    main()
