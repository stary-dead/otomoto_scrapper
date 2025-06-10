import pytest
import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
from unittest.mock import MagicMock, AsyncMock, patch
from callbacks import SubscribeFilterCallback, SubFilterBackCallback
from filters import KleinzengenFilter
from handlers.subscriptions_handler import (
    process_subscription_filter, 
    show_subscription_filters,
    update_subscription_filter,
    clear_subscription_filters,
    handle_sub_transmission_input,
    handle_sub_fuel_input,
    handle_sub_price_input,
    handle_sub_mileage_input,
    handle_sub_year_input,
    handle_sub_city_input
)

class TestSubscriptionFilters:
    
    @pytest.fixture
    def mock_user_filter(self):
        """Создает мок-объект фильтра пользователя"""
        filter_obj = KleinzengenFilter()
        return filter_obj
    
    @pytest.fixture
    def mock_callback_query(self):
        """Создает мок-объект callback query"""
        from_user = MagicMock(spec=types.User)
        from_user.id = 12345
        callback_query = AsyncMock(spec=types.CallbackQuery)
        callback_query.from_user = from_user
        callback_query.bot = AsyncMock()
        callback_query.message = AsyncMock()
        callback_query.answer = AsyncMock(return_value=None)
        return callback_query
    
    @pytest.fixture
    def mock_state(self):
        """Создает мок-объект состояния FSM"""
        state = AsyncMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"sub_filter": KleinzengenFilter()})
        return state
    
    @pytest.fixture
    def mock_message(self):
        """Создает мок-объект сообщения"""
        message = AsyncMock(spec=types.Message)
        message.from_user = MagicMock(spec=types.User)
        message.from_user.id = 12345
        message.text = "test_input"
        message.answer = AsyncMock()
        return message
    
    @pytest.mark.asyncio
    async def test_show_subscription_filters(self, mock_callback_query, mock_state):
        """Тестирует отображение доступных фильтров для подписки"""
        # Настраиваем фильтр с некоторыми заданными параметрами
        user_filter = KleinzengenFilter()
        user_filter._transmission = "Автомат"
        user_filter._fuel = "Diesel"
        mock_state.get_data = AsyncMock(return_value={"sub_filter": user_filter})
        
        # Вызываем функцию
        await show_subscription_filters(mock_callback_query, mock_state)
        
        # Проверяем, что вызван ответ на callback_query
        mock_callback_query.answer.assert_called_once()
        
        # Проверяем, что был отправлен ответ с описанием фильтров
        mock_callback_query.bot.send_message.assert_called_once()
        call_args = mock_callback_query.bot.send_message.call_args[0]
        
        # Проверяем, что в сообщении упоминаются текущие фильтры
        assert "Текущие фильтры:" in call_args[1]
        assert "Трансмиссия: Автомат" in call_args[1]
        assert "Топливо: Diesel" in call_args[1]
        
    @pytest.mark.asyncio
    async def test_process_transmission_filter(self, mock_callback_query, mock_state):
        """Тестирует обработку выбора фильтра трансмиссии"""
        # Создаем callback_data для выбора фильтра трансмиссии
        callback_data = SubscribeFilterCallback(filter_type="transmission")
        
        # Вызываем функцию
        await process_subscription_filter(mock_callback_query, callback_data, mock_state)
        
        # Проверяем, что было отправлено сообщение с запросом на выбор трансмиссии
        mock_callback_query.bot.send_message.assert_called_once()
        
        # Проверяем, что было установлено состояние для ввода трансмиссии
        mock_state.set_state.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_process_fuel_filter(self, mock_callback_query, mock_state):
        """Тестирует обработку выбора фильтра топлива"""
        # Создаем callback_data для выбора фильтра топлива
        callback_data = SubscribeFilterCallback(filter_type="fuel")
        
        # Вызываем функцию
        await process_subscription_filter(mock_callback_query, callback_data, mock_state)
        
        # Проверяем, что было отправлено сообщение с запросом на выбор топлива
        mock_callback_query.bot.send_message.assert_called_once()
        
        # Проверяем, что было установлено состояние для ввода типа топлива
        mock_state.set_state.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_price_filter(self, mock_callback_query, mock_state):
        """Тестирует обработку выбора фильтра цены"""
        # Создаем callback_data для выбора фильтра цены
        callback_data = SubscribeFilterCallback(filter_type="price")
        
        # Вызываем функцию
        await process_subscription_filter(mock_callback_query, callback_data, mock_state)
        
        # Проверяем, что было отправлено сообщение с запросом на ввод цены
        mock_callback_query.bot.send_message.assert_called_once()
        assert "диапазон" in mock_callback_query.bot.send_message.call_args[0][1].lower()
        
        # Проверяем, что было установлено состояние для ввода цены
        mock_state.set_state.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_mileage_filter(self, mock_callback_query, mock_state):
        """Тестирует обработку выбора фильтра пробега"""
        # Создаем callback_data для выбора фильтра пробега
        callback_data = SubscribeFilterCallback(filter_type="mileage")
        
        # Вызываем функцию
        await process_subscription_filter(mock_callback_query, callback_data, mock_state)
        
        # Проверяем, что было отправлено сообщение с запросом на ввод пробега
        mock_callback_query.bot.send_message.assert_called_once()
        assert "пробег" in mock_callback_query.bot.send_message.call_args[0][1].lower()
        
        # Проверяем, что было установлено состояние для ввода пробега
        mock_state.set_state.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_year_filter(self, mock_callback_query, mock_state):
        """Тестирует обработку выбора фильтра года выпуска"""
        # Создаем callback_data для выбора фильтра года
        callback_data = SubscribeFilterCallback(filter_type="year")
        
        # Вызываем функцию
        await process_subscription_filter(mock_callback_query, callback_data, mock_state)
        
        # Проверяем, что было отправлено сообщение с запросом на ввод года
        mock_callback_query.bot.send_message.assert_called_once()
        assert "год" in mock_callback_query.bot.send_message.call_args[0][1].lower()
        
        # Проверяем, что было установлено состояние для ввода года
        mock_state.set_state.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_transmission_input_valid(self, mock_message, mock_state):
        """Тестирует обработку корректного ввода типа трансмиссии"""
        # Устанавливаем корректный текст сообщения
        mock_message.text = "Автомат"
        
        # Заменяем вызов show_subscription_filters на заглушку
        with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
            mock_show_filters.return_value = None
            # Вызываем функцию
            await handle_sub_transmission_input(mock_message, mock_state)
        
        # Проверяем, что был сохранен новый фильтр
        mock_state.update_data.assert_called_once()
        
        # Проверяем, что было отправлено подтверждение
        mock_message.answer.assert_called_once()
        assert "Выбрана трансмиссия" in mock_message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_handle_transmission_input_invalid(self, mock_message, mock_state):
        """Тестирует обработку некорректного ввода типа трансмиссии"""
        # Устанавливаем некорректный текст сообщения
        mock_message.text = "Неправильная трансмиссия"
        
        # Вызываем функцию
        await handle_sub_transmission_input(mock_message, mock_state)
        
        # Проверяем, что не был сохранен новый фильтр
        mock_state.update_data.assert_not_called()
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called_once()
        assert "выберите из предложенного" in mock_message.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_price_filter_input_valid(self, mock_message, mock_state):
        """Тестирует обработку корректного ввода диапазона цен"""
        # Устанавливаем корректный текст сообщения для диапазона цен
        mock_message.text = "1000:5000"
        
        # Вызываем функцию
        with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
            mock_show_filters.return_value = None
            await handle_sub_price_input(mock_message, mock_state)
        
        # Проверяем, что был сохранен новый фильтр
        mock_state.update_data.assert_called_once()
        
        # Проверяем, что было отправлено подтверждение
        mock_message.answer.assert_called_once()
        assert "Установлена цена" in mock_message.answer.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_clear_subscription_filters(self, mock_callback_query, mock_state):
        """Тестирует очистку всех фильтров для подписки"""
        # Мокируем подписки с существующим пользователем
        with patch('handlers.subscriptions_handler.subscriptions', {12345: {"brand": "BMW", "model": "X5", "filter": KleinzengenFilter()}}):
            with patch('handlers.subscriptions_handler.asyncio.create_task') as mock_create_task:
                await clear_subscription_filters(mock_callback_query, mock_state)
                
                # Проверяем, что был сохранен пустой фильтр
                mock_state.update_data.assert_called_once()
                
                # Проверяем, что было отправлено сообщение об очистке фильтров
                mock_callback_query.bot.send_message.assert_called_once()
                assert "очищены" in mock_callback_query.bot.send_message.call_args[0][1].lower()
                
                # Проверяем, что был запущен мониторинг с новыми параметрами
                mock_create_task.assert_called_once()
                
    @pytest.mark.asyncio
    async def test_clear_subscription_filters_no_subscription(self, mock_callback_query, mock_state):
        """Тестирует очистку фильтров когда нет активной подписки"""
        # Мокируем пустые подписки
        with patch('handlers.subscriptions_handler.subscriptions', {}):
            await clear_subscription_filters(mock_callback_query, mock_state)
            
            # Проверяем, что фильтр не сохранялся
            mock_state.update_data.assert_not_called()
            
            # Проверяем сообщение об ошибке
            mock_callback_query.bot.send_message.assert_called_once()
            assert "нет активных подписок" in mock_callback_query.bot.send_message.call_args[0][1].lower()

    @pytest.mark.asyncio
    async def test_update_subscription_filter(self, mock_callback_query, mock_state):
        """Тестирует обновление фильтра для существующей подписки"""
        # Мок фильтра с настройками
        test_filter = KleinzengenFilter()
        test_filter._transmission = "Автомат"
        
        # Мокируем подписки с существующим пользователем и фильтром
        with patch('handlers.subscriptions_handler.subscriptions', 
                  {12345: {"brand": "BMW", "model": "X5", "filter": test_filter}}):
            with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
                mock_show_filters.return_value = None
                await update_subscription_filter(mock_callback_query, mock_state)
                
                # Проверяем, что были сохранены данные подписки в состоянии
                mock_state.update_data.assert_called_once()
                
                # Получаем переданные аргументы
                call_kwargs = mock_state.update_data.call_args.kwargs
                assert call_kwargs["subscribe_brand"] == "BMW"
                assert call_kwargs["subscribe_model"] == "X5" 
                assert call_kwargs["sub_filter"] == test_filter
                
                # Проверяем, что был вызван показ фильтров
                mock_show_filters.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_subscription_filter_no_subscription(self, mock_callback_query, mock_state):
        """Тестирует обновление фильтра когда нет активной подписки"""
        # Мокируем пустые подписки
        with patch('handlers.subscriptions_handler.subscriptions', {}):
            await update_subscription_filter(mock_callback_query, mock_state)
            
            # Проверяем, что данные не сохранялись
            mock_state.update_data.assert_not_called()
            
            # Проверяем сообщение об ошибке
            mock_callback_query.bot.send_message.assert_called_once()
            assert "нет активных подписок" in mock_callback_query.bot.send_message.call_args[0][1].lower()
    
    @pytest.mark.asyncio
    async def test_handle_fuel_input_valid(self, mock_message, mock_state):
        """Тестирует обработку корректного ввода типа топлива"""
        # Устанавливаем корректный текст сообщения
        mock_message.text = "Benzin"
        
        # Вызываем функцию
        with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
            mock_show_filters.return_value = None
            await handle_sub_fuel_input(mock_message, mock_state)
        
        # Проверяем, что был сохранен новый фильтр
        mock_state.update_data.assert_called_once()
        
        # Проверяем, что было отправлено подтверждение
        mock_message.answer.assert_called_once()
        assert "Выбран тип топлива" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_fuel_input_invalid(self, mock_message, mock_state):
        """Тестирует обработку некорректного ввода типа топлива"""
        # Устанавливаем некорректный текст сообщения
        mock_message.text = "Неправильное топливо"
        
        # Вызываем функцию
        await handle_sub_fuel_input(mock_message, mock_state)
        
        # Проверяем, что не был сохранен новый фильтр
        mock_state.update_data.assert_not_called()
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called_once()
        assert "выберите из предложенного" in mock_message.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_handle_mileage_input_valid(self, mock_message, mock_state):
        """Тестирует обработку корректного ввода пробега"""
        # Устанавливаем корректный текст сообщения для пробега
        mock_message.text = "10000:100000"
        
        # Вызываем функцию
        with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
            mock_show_filters.return_value = None
            await handle_sub_mileage_input(mock_message, mock_state)
        
        # Проверяем, что был сохранен новый фильтр
        mock_state.update_data.assert_called_once()
        
        # Проверяем, что было отправлено подтверждение
        mock_message.answer.assert_called_once()
        assert "Установлен пробег" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_mileage_input_invalid(self, mock_message, mock_state):
        """Тестирует обработку некорректного ввода пробега"""
        # Устанавливаем некорректный текст сообщения
        mock_message.text = "invalid_mileage"
        
        # Вызываем функцию
        await handle_sub_mileage_input(mock_message, mock_state)
        
        # Проверяем, что не был сохранен новый фильтр
        mock_state.update_data.assert_not_called()
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called_once()
        assert "корректный диапазон" in mock_message.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_handle_year_input_valid(self, mock_message, mock_state):
        """Тестирует обработку корректного ввода года выпуска"""
        # Устанавливаем корректный текст сообщения для года
        mock_message.text = "2010:2020"
        
        # Вызываем функцию
        with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
            mock_show_filters.return_value = None
            await handle_sub_year_input(mock_message, mock_state)
        
        # Проверяем, что был сохранен новый фильтр
        mock_state.update_data.assert_called_once()
        
        # Проверяем, что было отправлено подтверждение
        mock_message.answer.assert_called_once()
        assert "Установлен год выпуска" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_year_input_invalid(self, mock_message, mock_state):
        """Тестирует обработку некорректного ввода года выпуска"""
        # Устанавливаем некорректный текст сообщения
        mock_message.text = "invalid_year"
        
        # Вызываем функцию
        await handle_sub_year_input(mock_message, mock_state)
        
        # Проверяем, что не был сохранен новый фильтр
        mock_state.update_data.assert_not_called()
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called_once()
        assert "корректный диапазон" in mock_message.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_handle_city_input_valid(self, mock_message, mock_state):
        """Тестирует обработку корректного ввода города"""
        # Устанавливаем корректный текст сообщения для города
        mock_message.text = "Berlin"
        
        # Вызываем функцию
        with patch('handlers.subscriptions_handler.show_subscription_filters') as mock_show_filters:
            mock_show_filters.return_value = None
            await handle_sub_city_input(mock_message, mock_state)
        
        # Проверяем, что был сохранен новый фильтр
        mock_state.update_data.assert_called_once()
        
        # Проверяем, что было отправлено подтверждение
        mock_message.answer.assert_called_once()
        assert "Выбран город" in mock_message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_handle_city_input_invalid(self, mock_message, mock_state):
        """Тестирует обработку некорректного ввода города"""
        # Устанавливаем некорректный текст сообщения
        mock_message.text = "Несуществующий город"
        
        # Вызываем функцию
        await handle_sub_city_input(mock_message, mock_state)
        
        # Проверяем, что не был сохранен новый фильтр
        mock_state.update_data.assert_not_called()
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called_once()
        assert "выберите город из предложенного списка" in mock_message.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_process_save_filter_new_subscription(self, mock_callback_query, mock_state):
        """Тестирует сохранение фильтра для новой подписки"""
        # Создаем данные для фильтра и состояния
        user_filter = KleinzengenFilter()
        user_filter._transmission = "Автомат"
        user_filter._fuel = "Diesel"
        
        # Настраиваем состояние
        mock_state.get_data = AsyncMock(return_value={
            "sub_filter": user_filter,
            "subscribe_brand": "BMW",
            "subscribe_model": "X5"
        })
        
        # Создаем callback_data для сохранения фильтра
        callback_data = SubscribeFilterCallback(filter_type="save")
        
        # Мокируем пустые подписки и start_subscription
        with patch('handlers.subscriptions_handler.subscriptions', {}):
            with patch('handlers.subscriptions_handler.start_subscription') as mock_start_subscription:
                mock_start_subscription.return_value = None
                
                # Вызываем функцию
                await process_subscription_filter(mock_callback_query, callback_data, mock_state)
                  # Проверяем, что start_subscription был вызван с правильными параметрами
                mock_start_subscription.assert_called_once()
                call_args = mock_start_subscription.call_args[0]
                assert call_args[1] == mock_callback_query.from_user.id
                assert call_args[2] == "BMW"
                assert call_args[3] == "X5" 
                assert call_args[4] == user_filter
                
    @pytest.mark.asyncio
    async def test_process_save_filter_update_existing(self, mock_callback_query, mock_state):
        """Тестирует обновление фильтра для существующей подписки"""
        # Создаем данные для фильтра
        user_filter = KleinzengenFilter()
        user_filter._transmission = "Автомат"
        
        # Настраиваем состояние без brand/model (обновление существующей подписки)
        mock_state.get_data = AsyncMock(return_value={"sub_filter": user_filter})
        
        # Создаем callback_data для сохранения фильтра
        callback_data = SubscribeFilterCallback(filter_type="save")
        
        # Мокируем существующую подписку и обработку сохранения фильтра
        with patch('handlers.subscriptions_handler.subscriptions', 
                  {12345: {"brand": "BMW", "model": "X5", "filter": KleinzengenFilter()}}):
                
            # Вызываем функцию
            await process_subscription_filter(mock_callback_query, callback_data, mock_state)
            
            # Проверяем, что было отправлено сообщение об обновлении фильтров
            mock_callback_query.bot.send_message.assert_called_once()
            assert "обновлены" in mock_callback_query.bot.send_message.call_args[0][1].lower()
            
    @pytest.mark.asyncio
    async def test_process_clear_filter(self, mock_callback_query, mock_state):
        """Тестирует очистку фильтров в меню настроек фильтров"""
        # Создаем фильтры с настройками
        user_filter = KleinzengenFilter()
        user_filter._transmission = "Автомат"
        user_filter._fuel = "Diesel"
        mock_state.get_data = AsyncMock(return_value={"sub_filter": user_filter})
        
        # Создаем callback_data для очистки фильтров
        callback_data = SubscribeFilterCallback(filter_type="clear")
        
        # Мокируем существующую подписку
        with patch('handlers.subscriptions_handler.subscriptions', 
                  {12345: {"brand": "BMW", "model": "X5", "filter": user_filter}}):
                
            # Вызываем функцию
            await process_subscription_filter(mock_callback_query, callback_data, mock_state)
            
            # Проверяем, что был обновлен фильтр в состоянии на пустой
            mock_state.update_data.assert_called_once()
            
            # Проверяем, что было отправлено сообщение об очистке фильтров
            # В реализации send_message вызывается дважды, проверяем, что хотя бы один вызов содержит "очищены"
            assert mock_callback_query.bot.send_message.call_count >= 1
            
            # Проверим содержимое сообщений
            messages = [call_args[0][1] for call_args in mock_callback_query.bot.send_message.call_args_list]
            assert any("очищены" in message.lower() for message in messages)
    
    @pytest.mark.asyncio
    @patch('handlers.subscriptions_handler.check_for_updates')
    async def test_integration_with_scraper(self, mock_check_for_updates, mock_callback_query, mock_state):
        """Тестирует интеграцию с функцией проверки обновлений"""
        # Пользователь создает подписку с фильтрами
        from handlers.subscriptions_handler import start_subscription
        
        # Создаем фильтры
        user_filter = KleinzengenFilter()
        user_filter._transmission = "Автомат"
        user_filter._fuel = "Diesel"
        user_filter._price = "1000:5000"
        
        # Вызываем функцию старта подписки
        await start_subscription(mock_callback_query.bot, 12345, "BMW", "X5", user_filter)
        
        # Проверяем, что был запущен мониторинг с переданными параметрами
        mock_check_for_updates.assert_called_once_with(
            mock_callback_query.bot, 12345, "BMW", "X5"
        )
        
        # Проверяем, что было отправлено сообщение о начале мониторинга
        mock_callback_query.bot.send_message.assert_called_once()
        sent_message = mock_callback_query.bot.send_message.call_args[0][1]
        assert "Подписка на BMW X5 оформлена успешно" in sent_message
        
        # Проверяем, что в сообщении указаны активные фильтры
        assert "Трансмиссия: Автомат" in sent_message
        assert "Топливо: Diesel" in sent_message
        assert "Цена: 1000:5000" in sent_message
