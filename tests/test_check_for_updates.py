import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from aiogram import types
from handlers.subscriptions_handler import check_for_updates
from utils.brand import Brand
from filters import KleinzengenFilter
from articles import Article

class TestCheckForUpdates:
    
    @pytest.fixture
    def mock_bot(self):
        """Создает мок-объект бота"""
        bot = AsyncMock()
        bot.send_message = AsyncMock()
        return bot
    
    @pytest.fixture
    def mock_brand(self):
        """Создает мок-объект бренда"""
        brand = MagicMock(spec=Brand)
        brand.id = "bmw"
        brand.models = {"X5": "x5"}
        return brand
    
    @pytest.fixture
    def mock_article(self):
        """Создает мок-объект объявления"""
        article = MagicMock(spec=Article)
        article.title = "Test Article"
        article.description = "Test Description"
        article.price = "5000 €"
        article.main_image = "http://example.com/image.jpg"
        article.url = "http://example.com/article"
        # Настраиваем __eq__ для корректного сравнения
        article.__eq__.side_effect = lambda other: other.title == article.title
        return article
    
    @pytest.mark.asyncio
    @patch('handlers.subscriptions_handler.scrapper')
    @patch('handlers.subscriptions_handler.subscriptions')
    @patch('handlers.subscriptions_handler.asyncio.sleep', return_value=None)
    async def test_check_for_updates_with_filters(self, mock_sleep, mock_subscriptions, mock_scrapper, mock_bot, mock_brand, mock_article):
        """Тестирует функцию проверки обновлений с применением фильтров"""
        # Настраиваем пользователя и его подписку с фильтрами
        user_id = 12345
        brand_name = "BMW"
        model_name = "X5"
        
        # Создаем фильтр для пользователя
        user_filter = KleinzengenFilter()
        user_filter._transmission = "Автомат" 
        user_filter._fuel = "Diesel"
        
        # Настраиваем мок-подписки
        mock_subscriptions.__getitem__.return_value = {"brand": brand_name, "model": model_name, "filter": user_filter}
        mock_subscriptions.__contains__.side_effect = lambda key: key == user_id
        
        # Настраиваем мок-скраппер
        mock_scrapper.brands = {brand_name: mock_brand}
        mock_scrapper.get_articles = MagicMock(return_value=[mock_article])
        
        # Запускаем функцию проверки обновлений в отдельной задаче
        task = asyncio.create_task(check_for_updates(mock_bot, user_id, brand_name, model_name))
        
        # Даем задаче время на выполнение начального цикла
        await asyncio.sleep(0.1)
        
        # Отменяем задачу (иначе она будет работать бесконечно)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Проверяем, что фильтры были правильно применены к запросу
        mock_scrapper.get_articles.assert_called()
        
        # Получаем аргументы вызова get_articles
        filter_arg = mock_scrapper.get_articles.call_args[0][0]
        
        # Проверяем, что переданный фильтр содержит настройки пользователя
        assert filter_arg.transmission == "Автомат"
        assert filter_arg.fuel == "Diesel"
        assert filter_arg.brand['brand_id'] == mock_brand.id
        assert filter_arg.brand['model_id'] == mock_brand.models[model_name]
    
    @pytest.mark.asyncio
    @patch('handlers.subscriptions_handler.scrapper')
    @patch('handlers.subscriptions_handler.subscriptions')
    @patch('handlers.subscriptions_handler.asyncio.sleep', return_value=None)
    async def test_check_for_updates_new_articles(self, mock_sleep, mock_subscriptions, mock_scrapper, mock_bot, mock_brand):
        """Тестирует обработку новых объявлений"""
        # Настраиваем пользователя и его подписку
        user_id = 12345
        brand_name = "BMW"
        model_name = "X5"
        
        # Настраиваем мок-подписки
        mock_subscriptions.__getitem__.return_value = {"brand": brand_name, "model": model_name, "filter": None}
        mock_subscriptions.__contains__.side_effect = lambda key: key == user_id
        
        # Настраиваем мок-скраппер
        mock_scrapper.brands = {brand_name: mock_brand}
        
        # Создаем два набора объявлений: начальный и с новыми объявлениями
        old_article = MagicMock(spec=Article)
        old_article.title = "Old Article"
        old_article.main_image = "http://example.com/old_image.jpg"
        old_article.__eq__.side_effect = lambda other: other.title == old_article.title
        
        new_article = MagicMock(spec=Article)
        new_article.title = "New Article"
        new_article.main_image = "http://example.com/new_image.jpg"
        new_article.description = "Description"
        new_article.price = "10000 €"
        new_article.__eq__.side_effect = lambda other: other.title == new_article.title
        
        # Сначала возвращаем только старую статью, а затем обе статьи
        mock_scrapper.get_articles.side_effect = [[old_article], [old_article, new_article]]
        
        # Запускаем функцию проверки обновлений в отдельной задаче
        task = asyncio.create_task(check_for_updates(mock_bot, user_id, brand_name, model_name))
        
        # Даем задаче время на выполнение двух циклов
        await asyncio.sleep(0.2)
        
        # Отменяем задачу
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Проверяем, что бот отправил сообщение с новым объявлением
        assert mock_bot.send_photo.called
        # Проверяем параметры вызова send_photo
        call_args_list = mock_bot.send_photo.call_args_list
        # Проверяем содержимое сообщения для нового объявления
        assert any("New Article" in call.kwargs.get('caption', '') for call in call_args_list)
        
    @pytest.mark.asyncio
    @patch('handlers.subscriptions_handler.scrapper')
    @patch('handlers.subscriptions_handler.subscriptions')
    @patch('handlers.subscriptions_handler.asyncio.sleep', return_value=None)
    async def test_check_for_updates_filter_change(self, mock_sleep, mock_subscriptions, mock_scrapper, mock_bot, mock_brand):
        """Тестирует обработку изменения фильтров во время мониторинга"""
        # Настраиваем пользователя и его подписку
        user_id = 12345
        brand_name = "BMW"
        model_name = "X5"
        
        # Создаем начальный фильтр
        initial_filter = KleinzengenFilter()
        initial_filter._transmission = "Автомат"
        
        # Создаем обновленный фильтр
        updated_filter = KleinzengenFilter()
        updated_filter._transmission = "Механика"
        updated_filter._fuel = "Benzin"
        
        # Настраиваем мок-подписки с изменением фильтра
        subscription_data = {"brand": brand_name, "model": model_name, "filter": initial_filter}
        mock_subscriptions.__getitem__.return_value = subscription_data
        mock_subscriptions.__contains__.side_effect = lambda key: key == user_id
        
        # Настраиваем мок-скраппер
        mock_scrapper.brands = {brand_name: mock_brand}
        mock_scrapper.get_articles.return_value = []
        
        # Запускаем функцию проверки обновлений в отдельной задаче
        task = asyncio.create_task(check_for_updates(mock_bot, user_id, brand_name, model_name))
        
        # Даем задаче время на первоначальную инициализацию
        await asyncio.sleep(0.1)
        
        # Изменяем фильтр подписки
        subscription_data["filter"] = updated_filter
        
        # Даем задаче время на обнаружение изменения фильтра
        await asyncio.sleep(0.1)
        
        # Отменяем задачу
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Проверяем, что скраппер был вызван с обновленным фильтром
        # Получаем последний вызов get_articles
        last_call = mock_scrapper.get_articles.call_args_list[-1]
        filter_arg = last_call[0][0]
        
        # Проверяем, что переданный фильтр содержит обновленные настройки
        assert filter_arg.transmission == "Механика"
        assert filter_arg.fuel == "Benzin"
    
    @pytest.mark.asyncio
    @patch('handlers.subscriptions_handler.scrapper')
    @patch('handlers.subscriptions_handler.subscriptions')
    @patch('handlers.subscriptions_handler.asyncio.sleep', return_value=None)
    async def test_check_for_updates_error_handling(self, mock_sleep, mock_subscriptions, mock_scrapper, mock_bot, mock_brand):
        """Тестирует обработку ошибок в функции проверки обновлений"""
        # Настраиваем пользователя и его подписку
        user_id = 12345
        brand_name = "BMW"
        model_name = "X5"
        
        # Настраиваем мок-подписки
        mock_subscriptions.__getitem__.return_value = {"brand": brand_name, "model": model_name, "filter": None}
        mock_subscriptions.__contains__.side_effect = lambda key: key == user_id
        
        # Настраиваем мок-скраппер, вызывающий ошибку
        mock_scrapper.brands = {brand_name: mock_brand}
        mock_scrapper.get_articles.side_effect = Exception("Test error")
        
        # Запускаем функцию проверки обновлений
        await check_for_updates(mock_bot, user_id, brand_name, model_name)
        
        # Проверяем, что бот отправил сообщение об ошибке
        mock_bot.send_message.assert_called_once()
        error_message = mock_bot.send_message.call_args[0][1]
        assert "ошибка" in error_message.lower()
        assert brand_name in error_message
        assert model_name in error_message
