from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from scrappers import KleinzengenRequestsScrapper
from collections import defaultdict
from utils.brand import Brand
from articles import Article
from callbacks import SubscribeBrandCallback, SubscribeModelCallback, BrandCallback, SubscribeFilterCallback, SubFilterBackCallback
import asyncio
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
import re
from filters import KleinzengenFilter

# Используем мок для подписок, так как здесь нам не нужны реальные запросы к сайту
scrapper = KleinzengenRequestsScrapper()
subscriptions = defaultdict(lambda: {"brand": None, "model": None, "filter": None})

class SubscribeFilterState(StatesGroup):
    transmission = State()
    fuel = State()
    price = State()
    mileage = State()
    year = State()
    city = State()

def register_handlers(dp):
    dp.callback_query.register(process_subscribe, lambda c: c.data == "subscribe")
    dp.callback_query.register(process_choose_brand, SubscribeBrandCallback.filter())
    dp.callback_query.register(process_choose_model, SubscribeModelCallback.filter())
    dp.callback_query.register(process_unsubscribe, lambda c: c.data == "unsubscribe")
    dp.callback_query.register(process_my_subscriptions, lambda c: c.data == "my_subscriptions")
    
    # Обработчики для фильтрации подписок
    dp.callback_query.register(show_subscription_filters, lambda c: c.data == "show_sub_filters")
    dp.callback_query.register(process_subscription_filter, SubscribeFilterCallback.filter())
    dp.callback_query.register(back_to_subscription, SubFilterBackCallback.filter())
    # Убрана строка с update_subscription_filter, так как такая функция не существует
    dp.callback_query.register(clear_subscription_filters, lambda c: c.data == "clear_sub_filters")
    
    # Обработчики ввода для фильтров
    dp.message.register(handle_sub_transmission_input, StateFilter(SubscribeFilterState.transmission))
    dp.message.register(handle_sub_fuel_input, StateFilter(SubscribeFilterState.fuel))
    dp.message.register(handle_sub_price_input, StateFilter(SubscribeFilterState.price))
    dp.message.register(handle_sub_mileage_input, StateFilter(SubscribeFilterState.mileage))
    dp.message.register(handle_sub_year_input, StateFilter(SubscribeFilterState.year))
    dp.message.register(handle_sub_city_input, StateFilter(SubscribeFilterState.city))

async def process_subscribe(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    # Показываем выбор брендов
    bot = callback_query.bot
    btns = []
    for brand in scrapper.brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=SubscribeBrandCallback(brand=brand).pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Выберите бренд:", reply_markup=inline_kb)

async def process_unsubscribe(callback_query: types.CallbackQuery):
    bot = callback_query.bot
    user_id = callback_query.from_user.id
    
    await callback_query.answer()
    
    if user_id in subscriptions:
        # Получаем информацию о подписке перед удалением
        subscription_info = subscriptions[user_id]
        brand = subscription_info["brand"]
        model = subscription_info["model"]
        
        # Удаляем подписку
        del subscriptions[user_id]
        
        # Создаем кнопку для повторной подписки
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оформить новую подписку", callback_data="subscribe")],
        ])
        
        await bot.send_message(
            user_id, 
            f"Вы отписались от уведомлений о новых объявлениях {brand} {model}.\n"
            f"Мониторинг объявлений остановлен.", 
            reply_markup=inline_kb
        )
    else:
        # Если подписки нет, предлагаем оформить
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оформить подписку", callback_data="subscribe")],
        ])
        
        await bot.send_message(
            user_id, 
            "У вас нет активных подписок на обновления.", 
            reply_markup=inline_kb
        )

async def process_choose_brand(callback_query: types.CallbackQuery, callback_data: BrandCallback, state: FSMContext):
    brand = callback_data.brand
    await callback_query.answer()
    await state.update_data(subscribe_brand=brand)
    bot = callback_query.bot
    # Показываем выбор моделей
    models = get_brand_models(brand)
    btns = []
    for model in models:
        btns.append([InlineKeyboardButton(text=model, callback_data=SubscribeModelCallback(model=model, brand=brand).pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Выберите модель:", reply_markup=inline_kb)


async def process_choose_model(callback_query: types.CallbackQuery, callback_data: SubscribeModelCallback, state: FSMContext):
    model = callback_data.model
    bot = callback_query.bot
    brand = callback_data.brand
    user_id = callback_query.from_user.id
    
    await callback_query.answer()
    
    # Сохраняем выбранный бренд и модель в состоянии
    await state.update_data(subscribe_brand=brand, subscribe_model=model)
    
    # Предлагаем пользователю настроить дополнительные фильтры или оформить подписку сразу
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подписаться без фильтров", callback_data=SubscribeFilterCallback(filter_type="save").pack())],
        [InlineKeyboardButton(text="⚙️ Настроить фильтры", callback_data="show_sub_filters")],
    ])
    
    await bot.send_message(
        user_id,
        f"Вы выбрали подписку на {brand} {model}.\n\n"
        f"Вы можете подписаться сразу или настроить дополнительные фильтры (трансмиссия, топливо, цена и т.д.).",
        reply_markup=inline_kb
    )

async def check_for_updates(bot, user_id, brand_name, model_name):
    try:
        brand = scrapper.brands[brand_name]
        
        # Получаем информацию о подписке пользователя, включая фильтры
        user_subscription = subscriptions[user_id]
        stored_filter = user_subscription.get("filter")
        
        # Если у пользователя есть сохраненный фильтр, используем его, иначе создаем новый
        if stored_filter:
            user_filter = stored_filter
            # Устанавливаем бренд и модель в фильтре с правильными ключами
            user_filter._brand = {
                'brand_id': brand.id,
                'model_id': brand.models[model_name] if model_name != "all" else None
            }
            user_filter._page = 1
        else:
            # Создаем новый фильтр для поиска автомобилей
            user_filter = KleinzengenFilter(page=1)
            # Устанавливаем бренд и модель в фильтре с правильными ключами
            user_filter._brand = {
                'brand_id': brand.id,
                'model_id': brand.models[model_name] if model_name != "all" else None
            }
        
        # Формируем информацию о фильтрах для лога
        filters_info = []
        if user_filter.transmission:
            filters_info.append(f"трансмиссия: {user_filter.transmission}")
        if user_filter.fuel:
            filters_info.append(f"топливо: {user_filter.fuel}")
        if user_filter.price:
            filters_info.append(f"цена: {user_filter.price}")
        if user_filter.milleage:
            filters_info.append(f"пробег: {user_filter.milleage}")
        if user_filter.year:
            filters_info.append(f"год: {user_filter.year}")
        if user_filter.city:
            filters_info.append(f"город: {user_filter.city}")
        
        filters_str = ", ".join(filters_info)
        print(f"Запущена подписка для пользователя {user_id} на {brand_name} {model_name}" + 
              (f" с фильтрами: {filters_str}" if filters_str else ""))
        print(f"Создан фильтр с брендом ID: {brand.id} и моделью: {brand.models.get(model_name, 'all')}")
        
        try:            # Дополнительное логирование для отладки
            print(f"Параметры фильтра: {user_filter._brand}")
            try:
                url = user_filter.get_web_url()  # Добавляем скобки для вызова метода
                print(f"URL запроса: {url}")
            except Exception as url_error:
                print(f"Ошибка при формировании URL: {url_error}")
              # Получаем начальный список статей с более надежной обработкой ошибок
            try:
                old_articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter))
                articles_count = len(old_articles) if old_articles else 0
                print(f"Получено {articles_count} начальных объявлений")
            except Exception as article_error:
                print(f"Ошибка при получении статей: {article_error}")
                old_articles = []
                articles_count = 0
            
            # Формируем сообщение с учетом фильтров
            filters_msg = ""
            if filters_str:
                filters_msg = f"\nФильтры: {filters_str}"
                
            # Сразу отправим пользователю уведомление о начале мониторинга
            await bot.send_message(
                user_id, 
                f"Мониторинг объявлений для {brand_name} {model_name} запущен.{filters_msg}\n"
                f"Получено {len(old_articles) if old_articles else 0} объявлений.\n"
                f"Вы будете получать уведомления о новых объявлениях."
            )
        except Exception as e:
            print(f"Ошибка при получении начальных объявлений: {e}")
            await bot.send_message(
                user_id,
                f"Возникла ошибка при запуске мониторинга объявлений для {brand_name} {model_name}.\n"
                f"Попробуйте позже или выберите другую модель."
            )
            return
        
        # Начальная задержка перед первой проверкой
        await asyncio.sleep(10)
          # Главный цикл проверки новых объявлений
        while user_id in subscriptions:
            try:
                # Проверяем, не изменились ли параметры подписки
                current_subscription = subscriptions[user_id]
                current_brand = current_subscription["brand"]
                current_model = current_subscription["model"]
                current_filter = current_subscription.get("filter")
                
                # Если бренд или модель изменились, обновляем фильтр
                if current_brand != brand_name or current_model != model_name:
                    print(f"Обнаружено изменение подписки для пользователя {user_id}: с {brand_name} {model_name} на {current_brand} {current_model}")
                    return  # Завершаем этот цикл, запустится новый с новыми параметрами
                
                # Если фильтр изменился, обновляем его
                if current_filter is not stored_filter:
                    print(f"Обнаружено изменение фильтров для подписки пользователя {user_id}")
                    user_filter = current_filter if current_filter else user_filter
                    
                # Получаем новые артикулы с текущим фильтром
                print(f"Получение новых статей для пользователя {user_id} с фильтром для {current_brand} {current_model}")
                new_articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter))
                
                if new_articles is None:
                    print(f"Ошибка получения данных для пользователя {user_id}")
                    await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой
                    continue
                    
                # Логируем количество статей
                print(f"Проверка для пользователя {user_id}: получено {len(new_articles)} объявлений")
                
                # Сравниваем с предыдущими
                if old_articles and new_articles != old_articles:
                    # Собираем новые артикулы, которых не было в старом списке
                    new_articles_list = [article for article in new_articles if article not in old_articles]
                    new_count = len(new_articles_list)
                    
                    if new_count > 0:
                        print(f"Найдено {new_count} новых объявлений для пользователя {user_id}")
                        
                        # Отправляем новые артикулы пользователю, но не более 5 за раз
                        for i, article in enumerate(new_articles_list[:5]):
                            await show_article(user_id, article, bot, None)
                            # Небольшая задержка между отправкой сообщений
                            await asyncio.sleep(1)
                            
                        # Если новых объявлений больше 5, сообщаем о них
                        if new_count > 5:
                            await bot.send_message(
                                user_id,
                                f"Найдено еще {new_count - 5} новых объявлений. "
                                f"Чтобы просмотреть все объявления, используйте команду поиска."
                            )
                    
                        print(f"Отправлено {min(new_count, 5)} новых объявлений пользователю {user_id}")
                    
                    # Обновляем список старых артикулов
                    old_articles = new_articles
            
            except Exception as e:
                print(f"Ошибка при проверке обновлений для пользователя {user_id}: {e}")
            
            # Ждем указанное время перед следующей проверкой (5 минут)
            await asyncio.sleep(300)
        
        # Если пользователь отписался
        print(f"Подписка для пользователя {user_id} на {brand_name} {model_name} завершена")
    
    except Exception as e:
        print(f"Критическая ошибка в check_for_updates для {user_id} на {brand_name} {model_name}: {e}")
        try:
            await bot.send_message(
                user_id,
                f"Произошла ошибка при работе подписки на {brand_name} {model_name}.\n"
                f"Пожалуйста, оформите подписку заново."
            )
        except:
            pass

async def show_article(user_id: int, article:Article, bot,  index:int | None):
    """Показывает объявление пользователю с учетом фильтров и подписок"""
    try:
        image_url = article.main_image
        title = article.title
        subtitle = article.description
        price = article.price
        caption = f"{title}\n\n{subtitle}\n\n{price}"
    except Exception as e:
        print(f"Error displaying article: {e}")
        caption = "Error displaying article details"
        image_url = None
        
        # Добавляем информацию о подписке, если это уведомление о новом объявлении (index=None)
        if index is None and user_id in subscriptions:
            subscription_info = subscriptions[user_id]
            brand = subscription_info["brand"]
            model = subscription_info["model"]
            user_filter = subscription_info.get("filter")
            
            filter_info = ""
            if user_filter:
                active_filters = []
                if user_filter.transmission:
                    active_filters.append(f"трансмиссия: {user_filter.transmission}")
                if user_filter.fuel:
                    active_filters.append(f"топливо: {user_filter.fuel}")
                if user_filter.price:
                    active_filters.append(f"цена: {user_filter.price}")
                if user_filter.milleage:
                    active_filters.append(f"пробег: {user_filter.milleage}")
                if user_filter.year:
                    active_filters.append(f"год: {user_filter.year}")
                if user_filter.city:
                    active_filters.append(f"город: {user_filter.city}")
                    
                if active_filters:
                    filter_info = " | ".join(active_filters)
                    
            subscription_info = f"\n\n🔔 Новое объявление для подписки: {brand} {model}"
            if filter_info:
                subscription_info += f"\nФильтры: {filter_info}"
                
            caption += subscription_info
    
    btns = []
    if index is not None:
        if index > 0:
            btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
        btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns])
        await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)
    else:
        # Для уведомлений по подписке добавляем кнопку для открытия сайта, если есть URL статьи
        url = getattr(article, 'url', None)
        btns = []
        
        if url:
            btns.append([InlineKeyboardButton(text="Открыть на сайте", url=url)])
            
        if user_id in subscriptions:
            btns.append([InlineKeyboardButton(text="Настроить фильтры", callback_data="show_sub_filters")])
            btns.append([InlineKeyboardButton(text="Отписаться", callback_data="unsubscribe")])
        
        inline_kb = InlineKeyboardMarkup(inline_keyboard=btns) if btns else None
        await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)

def get_brand_models(brand_name: str):
    brand = scrapper.brands.get(brand_name)
    if brand:
        return brand.get_models()
    else:
        return None

async def process_my_subscriptions(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    bot = callback_query.bot
    user_id = callback_query.from_user.id

    if user_id in subscriptions:
        # Если пользователь уже подписан, показываем информацию
        subscription_info = subscriptions[user_id]
        brand = subscription_info["brand"]
        model = subscription_info["model"]
        user_filter = subscription_info.get("filter")
        
        # Сохраняем информацию о подписке в состоянии
        await state.update_data(subscribe_brand=brand, subscribe_model=model, sub_filter=user_filter)
        
        # Формируем информацию о фильтрах, если они есть
        filters_info = ""
        if user_filter:
            filters_list = []
            if user_filter.transmission:
                filters_list.append(f"🔹 Трансмиссия: {user_filter.transmission}")
            if user_filter.fuel:
                filters_list.append(f"🔹 Топливо: {user_filter.fuel}")
            if user_filter.price:
                filters_list.append(f"🔹 Цена: {user_filter.price}")
            if user_filter.milleage:
                filters_list.append(f"🔹 Пробег: {user_filter.milleage}")
            if user_filter.year:
                filters_list.append(f"🔹 Год выпуска: {user_filter.year}")
            if user_filter.city:
                filters_list.append(f"🔹 Город: {user_filter.city}")
                
            if filters_list:
                filters_info = "\n\nАктивные фильтры:\n" + "\n".join(filters_list)
        
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Изменить подписку", callback_data="subscribe")],
            [InlineKeyboardButton(text="⚙️ Настроить фильтры", callback_data="show_sub_filters")],
            [InlineKeyboardButton(text="🗑️ Очистить все фильтры", callback_data="clear_sub_filters")],
            [InlineKeyboardButton(text="❌ Отписаться", callback_data="unsubscribe")],
        ])
        
        await bot.send_message(
            user_id, 
            f"У вас есть активная подписка на автомобиль {brand} {model}.{filters_info}\n"
            f"Вы будете получать уведомления о новых объявлениях.", 
            reply_markup=inline_kb
        )
    else:
        # Если подписок нет, предлагаем подписаться
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оформить подписку", callback_data="subscribe")],
        ])
        
        await bot.send_message(
            user_id,
            "У вас пока нет активных подписок на автомобили.\n"
            "Подписавшись, вы будете получать уведомления о новых объявлениях.", 
            reply_markup=inline_kb
        )

class SubscriptionException(Exception):
    """Исключение, связанное с ошибками подписки"""
    pass

async def show_subscription_filters(callback_query: types.CallbackQuery, state: FSMContext):
    """Показывает доступные фильтры для подписки"""
    bot = callback_query.bot
    await callback_query.answer()
    
    # Получаем данные о текущем фильтре, если они есть
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    # Подготавливаем описание текущих фильтров
    filter_description = "Текущие фильтры:\n"
    has_filters = False
    
    if user_filter:
        if user_filter.transmission:
            filter_description += f"✓ Трансмиссия: {user_filter.transmission}\n"
            has_filters = True
        if user_filter.fuel:
            filter_description += f"✓ Топливо: {user_filter.fuel}\n"
            has_filters = True
        if user_filter.price:
            filter_description += f"✓ Цена: {user_filter.price}\n"
            has_filters = True
        if user_filter.milleage:
            filter_description += f"✓ Пробег: {user_filter.milleage}\n"
            has_filters = True
        if user_filter.year:
            filter_description += f"✓ Год: {user_filter.year}\n"
            has_filters = True
        if user_filter.city:
            filter_description += f"✓ Город: {user_filter.city}\n"
            has_filters = True
            
    if not has_filters:
        filter_description = "В данный момент фильтры не установлены. Выберите фильтры ниже:"
    
    # Создаем клавиатуру для фильтров
    filters_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Трансмиссия", callback_data=SubscribeFilterCallback(filter_type="transmission").pack())],
            [InlineKeyboardButton(text="⛽ Топливо", callback_data=SubscribeFilterCallback(filter_type="fuel").pack())],
            [InlineKeyboardButton(text="💰 Цена", callback_data=SubscribeFilterCallback(filter_type="price").pack())],
            [InlineKeyboardButton(text="🛣️ Пробег", callback_data=SubscribeFilterCallback(filter_type="mileage").pack())],
            [InlineKeyboardButton(text="📅 Год выпуска", callback_data=SubscribeFilterCallback(filter_type="year").pack())],
            [InlineKeyboardButton(text="🏙️ Город", callback_data=SubscribeFilterCallback(filter_type="city").pack())],
            [InlineKeyboardButton(text="🗑️ Очистить фильтры", callback_data=SubscribeFilterCallback(filter_type="clear").pack())],
            [InlineKeyboardButton(text="💾 Сохранить фильтры", callback_data=SubscribeFilterCallback(filter_type="save").pack())],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=SubFilterBackCallback().pack())]
        ]
    )
    
    await bot.send_message(
        callback_query.from_user.id, 
        filter_description, 
        reply_markup=filters_kb
    )
async def clear_subscription_filters(callback_query: types.CallbackQuery, state: FSMContext):
    """Очищает все фильтры подписки"""
    bot = callback_query.bot
    user_id = callback_query.from_user.id
    await callback_query.answer()
    
    # Очищаем фильтры в состоянии
    user_filter = KleinzengenFilter()
    await state.update_data(sub_filter=user_filter)
    
    # Если пользователь уже подписан, обновляем фильтр в подписке
    if user_id in subscriptions:
        subscription_info = subscriptions[user_id]
        brand_name = subscription_info["brand"]
        model_name = subscription_info["model"]
        subscriptions[user_id]["filter"] = None
        
        await bot.send_message(
            user_id,
            f"Все фильтры для подписки на {brand_name} {model_name} очищены ✅"
        )
    else:
        await bot.send_message(user_id, "Все фильтры очищены ✅")
    
    # Показываем обновленное меню фильтров
    await show_subscription_filters_direct(bot, user_id, state)
    
async def process_subscription_filter(callback_query: types.CallbackQuery, callback_data: SubscribeFilterCallback, state: FSMContext):
    """Обрабатывает выбор фильтра"""
    bot = callback_query.bot
    filter_type = callback_data.filter_type
    user_id = callback_query.from_user.id
    
    await callback_query.answer()
    
    # Получаем текущий фильтр из состояния
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
        await state.update_data(sub_filter=user_filter)
    
    if filter_type == "transmission":
        # Обрабатываем выбор трансмиссии
        keyboard = [[KeyboardButton(text=x)] for x in user_filter.TRANSMISSION_CHOICES.keys()]
        reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(user_id, "Выберите тип трансмиссии:", reply_markup=reply_keyboard)
        await state.set_state(SubscribeFilterState.transmission)
        
    elif filter_type == "fuel":
        # Обрабатываем выбор топлива
        keyboard = [[KeyboardButton(text=x)] for x in user_filter.FUEL_CHOICES.keys()]
        reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(user_id, "Выберите тип топлива:", reply_markup=reply_keyboard)
        await state.set_state(SubscribeFilterState.fuel)
        
    elif filter_type == "price":
        # Обрабатываем выбор цены
        await bot.send_message(user_id, "Введите максимальную цену или введите диапазон через двоеточие\nНапример: 1000:5000")
        await state.set_state(SubscribeFilterState.price)
        
    elif filter_type == "mileage":
        # Обрабатываем выбор пробега
        await bot.send_message(user_id, "Введите максимальный пробег или введите диапазон через двоеточие\nНапример: 10000:100000")
        await state.set_state(SubscribeFilterState.mileage)
        
    elif filter_type == "year":
        # Обрабатываем выбор года
        await bot.send_message(user_id, "Введите максимальный год или введите диапазон через двоеточие\nНапример: 2010:2020")
        await state.set_state(SubscribeFilterState.year)
        
    elif filter_type == "city":
        # Обрабатываем выбор города
        keyboard = [[KeyboardButton(text=x)] for x in user_filter.CITY_CHOICES.keys()]
        reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(user_id, "Выберите город:", reply_markup=reply_keyboard)
        await state.set_state(SubscribeFilterState.city)
        
    elif filter_type == "clear":
        # Очищаем все фильтры
        user_filter = KleinzengenFilter()
        await state.update_data(sub_filter=user_filter)
        await bot.send_message(user_id, "Все фильтры очищены ✅")
        
        # Если пользователь уже подписан, обновляем фильтр в подписке
        if user_id in subscriptions:
            subscription_info = subscriptions[user_id]
            brand_name = subscription_info["brand"]
            model_name = subscription_info["model"]
            subscriptions[user_id]["filter"] = None
            
            await bot.send_message(
                user_id,
                f"Все фильтры для подписки на {brand_name} {model_name} очищены ✅"
            )
        
    elif filter_type == "save":
        # Сохраняем подписку с фильтрами
        brand_name = state_data.get("subscribe_brand")
        model_name = state_data.get("subscribe_model")
        
        if not brand_name or not model_name:
            # Проверяем, может быть это обновление существующей подписки
            if user_id in subscriptions:
                subscription_info = subscriptions[user_id]
                brand_name = subscription_info["brand"]
                model_name = subscription_info["model"]
                
                # Обновляем фильтры в существующей подписке
                subscriptions[user_id]["filter"] = user_filter
                
                # Формируем сообщение с обновленными фильтрами
                filters_info = []
                if user_filter.transmission:
                    filters_info.append(f"трансмиссия: {user_filter.transmission}")
                if user_filter.fuel:
                    filters_info.append(f"топливо: {user_filter.fuel}")
                if user_filter.price:
                    filters_info.append(f"цена: {user_filter.price}")
                if user_filter.milleage:
                    filters_info.append(f"пробег: {user_filter.milleage}")
                if user_filter.year:
                    filters_info.append(f"год: {user_filter.year}")
                if user_filter.city:
                    filters_info.append(f"город: {user_filter.city}")
                
                filters_str = ", ".join(filters_info)
                
                await bot.send_message(
                    user_id,
                    f"Фильтры для подписки на {brand_name} {model_name} обновлены." +
                    (f"\nНовые фильтры: {filters_str}" if filters_str else "\nВсе фильтры сброшены.")
                )
                return
            else:
                await bot.send_message(user_id, "Пожалуйста, сначала выберите бренд и модель автомобиля.")
                return
        
        # Запускаем подписку с фильтрами
        await start_subscription(bot, user_id, brand_name, model_name, user_filter)

async def start_subscription(bot, user_id, brand_name, model_name, user_filter=None):
    """Запускает подписку с выбранными параметрами"""
    # Если пользователь уже подписан, удаляем старую подписку
    if user_id in subscriptions:
        old_subscription = subscriptions[user_id]
        old_brand = old_subscription["brand"]
        old_model = old_subscription["model"]
        
        # Удаляем старую подписку
        del subscriptions[user_id]
        
        # Уведомляем пользователя о смене подписки
        await bot.send_message(
            user_id, 
            f"Ваша предыдущая подписка на {old_brand} {old_model} отменена.\n"
            f"Создана новая подписка на {brand_name} {model_name}."
        )
    
    # Создаем новую подписку
    subscriptions[user_id] = {"brand": brand_name, "model": model_name, "filter": user_filter}
    
    # Информируем пользователя
    filters_info = ""
    if user_filter:
        if user_filter.transmission:
            filters_info += f"\n- Трансмиссия: {user_filter.transmission}"
        if user_filter.fuel:
            filters_info += f"\n- Топливо: {user_filter.fuel}"
        if user_filter.price:
            filters_info += f"\n- Цена: {user_filter.price}"
        if user_filter.milleage:
            filters_info += f"\n- Пробег: {user_filter.milleage}"
        if user_filter.year:
            filters_info += f"\n- Год выпуска: {user_filter.year}"
        if user_filter.city:
            filters_info += f"\n- Город: {user_filter.city}"
    
    await bot.send_message(
        user_id, 
        f"Подписка на {brand_name} {model_name} оформлена успешно!{filters_info}\n"
        f"Система начинает мониторинг объявлений. Вы будете получать уведомления о новых объявлениях."
    )
    
    # Запускаем проверку в фоновом режиме
    asyncio.create_task(check_for_updates(bot, user_id, brand_name, model_name))
        
async def back_to_subscription(callback_query: types.CallbackQuery, state: FSMContext):
    """Возвращает к основному меню подписки"""
    bot = callback_query.bot
    user_id = callback_query.from_user.id
    await callback_query.answer()
    
    # Очищаем состояние
    await state.clear()
    
    # Проверяем наличие активных подписок
    has_subscription = user_id in subscriptions
    
    # Отправляем сообщение о возможности оформления подписки
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оформить новую подписку", callback_data="subscribe")],
        [InlineKeyboardButton(text="Мои подписки", callback_data="my_subscriptions")],
    ])
    
    await bot.send_message(
        user_id, 
        "Выберите действие для управления подписками:" + 
        ("\nУ вас уже есть активные подписки." if has_subscription else ""), 
        reply_markup=inline_kb
    )

# Обработчики ввода для фильтров
async def handle_sub_transmission_input(message: types.Message, state: FSMContext):
    """Обрабатывает ввод типа трансмиссии"""
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
    
    if user_input in user_filter.TRANSMISSION_CHOICES.keys():
        user_filter._transmission = user_input
        await state.update_data(sub_filter=user_filter)
        
        await message.answer(f"Выбрана трансмиссия: {user_input} ✅", reply_markup=ReplyKeyboardRemove())
        
        # Вызываем функцию напрямую с ботом БЕЗ очистки состояния
        await show_subscription_filters_direct(message.bot, message.from_user.id, state)
    else:
        await message.answer("Пожалуйста, выберите из предложенного: Автомат или Механика.")

async def handle_sub_fuel_input(message: types.Message, state: FSMContext):
    """Обрабатывает ввод типа топлива"""
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
    
    if user_input in user_filter.FUEL_CHOICES.keys():
        user_filter._fuel = user_input
        await state.update_data(sub_filter=user_filter)
        
        await message.answer(f"Выбран тип топлива: {user_input} ✅", reply_markup=ReplyKeyboardRemove())
        
        # Вызываем функцию напрямую с ботом БЕЗ очистки состояния
        await show_subscription_filters_direct(message.bot, message.from_user.id, state)
    else:
        await message.answer("Пожалуйста, выберите из предложенного списка.")

async def handle_sub_price_input(message: types.Message, state: FSMContext):
    """Обрабатывает ввод цены"""
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
        
    if re.match(r'^\d+(:\d+)?$', user_input):
        if len(user_input.split(':')) == 2:
            answer = user_input
        else:
            answer = ':' + user_input
        
        user_filter._price = answer
        await state.update_data(sub_filter=user_filter)
        
        await message.answer(f"Установлена цена: {user_input} €✅", reply_markup=ReplyKeyboardRemove())
        
        # Вызываем функцию напрямую с ботом БЕЗ очистки состояния
        await show_subscription_filters_direct(message.bot, message.from_user.id, state)
    else:
        await message.answer("Пожалуйста, введите корректный диапазон цен.")

async def handle_sub_mileage_input(message: types.Message, state: FSMContext):
    """Обрабатывает ввод пробега"""
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
        
    if re.match(r'^\d+(:\d+)?$', user_input):
        if len(user_input.split(':')) == 2:
            answer = user_input
        else:
            answer = ':' + user_input
        
        user_filter._milleage = answer
        await state.update_data(sub_filter=user_filter)
        
        await message.answer(f"Установлен пробег: {user_input} км✅", reply_markup=ReplyKeyboardRemove())
        
        # Вызываем функцию напрямую с ботом БЕЗ очистки состояния
        await show_subscription_filters_direct(message.bot, message.from_user.id, state)
    else:
        await message.answer("Пожалуйста, введите корректный диапазон пробега.")

async def handle_sub_year_input(message: types.Message, state: FSMContext):
    """Обрабатывает ввод года"""
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
        
    if re.match(r'^\d+(:\d+)?$', user_input):
        if len(user_input.split(':')) == 2:
            answer = user_input
        else:
            answer = ':' + user_input
        
        user_filter._year = answer
        await state.update_data(sub_filter=user_filter)
        
        await message.answer(f"Установлен год выпуска: {user_input} ✅", reply_markup=ReplyKeyboardRemove())
        
        # Вызываем функцию напрямую с ботом БЕЗ очистки состояния
        await show_subscription_filters_direct(message.bot, message.from_user.id, state)
    else:
        await message.answer("Пожалуйста, введите корректный диапазон годов выпуска.")

async def handle_sub_city_input(message: types.Message, state: FSMContext):
    """Обрабатывает ввод города"""
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    if not user_filter:
        user_filter = KleinzengenFilter()
    
    if user_input in user_filter.CITY_CHOICES.keys():
        user_filter._city = user_input
        await state.update_data(sub_filter=user_filter)
        
        await message.answer(f"Выбран город: {user_input} ✅", reply_markup=ReplyKeyboardRemove())
        
        # Вызываем функцию напрямую с ботом БЕЗ очистки состояния
        await show_subscription_filters_direct(message.bot, message.from_user.id, state)
    else:
        await message.answer("Пожалуйста, выберите город из предложенного списка.")

async def show_subscription_filters_direct(bot, user_id: int, state: FSMContext):
    """Показывает доступные фильтры для подписки (прямой вызов без callback_query)"""
    
    # Получаем данные о текущем фильтре, если они есть
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("sub_filter")
    
    # Подготавливаем описание текущих фильтров
    filter_description = "Текущие фильтры:\n"
    has_filters = False
    
    if user_filter:
        if user_filter.transmission:
            filter_description += f"✓ Трансмиссия: {user_filter.transmission}\n"
            has_filters = True
        if user_filter.fuel:
            filter_description += f"✓ Топливо: {user_filter.fuel}\n"
            has_filters = True
        if user_filter.price:
            filter_description += f"✓ Цена: {user_filter.price}\n"
            has_filters = True
        if user_filter.milleage:
            filter_description += f"✓ Пробег: {user_filter.milleage}\n"
            has_filters = True
        if user_filter.year:
            filter_description += f"✓ Год: {user_filter.year}\n"
            has_filters = True
        if user_filter.city:
            filter_description += f"✓ Город: {user_filter.city}\n"
            has_filters = True
            
    if not has_filters:
        filter_description = "В данный момент фильтры не установлены. Выберите фильтры ниже:"
    
    # Создаем клавиатуру для фильтров
    filters_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Трансмиссия", callback_data=SubscribeFilterCallback(filter_type="transmission").pack())],
            [InlineKeyboardButton(text="⛽ Топливо", callback_data=SubscribeFilterCallback(filter_type="fuel").pack())],
            [InlineKeyboardButton(text="💰 Цена", callback_data=SubscribeFilterCallback(filter_type="price").pack())],
            [InlineKeyboardButton(text="🛣️ Пробег", callback_data=SubscribeFilterCallback(filter_type="mileage").pack())],
            [InlineKeyboardButton(text="📅 Год выпуска", callback_data=SubscribeFilterCallback(filter_type="year").pack())],
            [InlineKeyboardButton(text="🏙️ Город", callback_data=SubscribeFilterCallback(filter_type="city").pack())],
            [InlineKeyboardButton(text="🗑️ Очистить фильтры", callback_data=SubscribeFilterCallback(filter_type="clear").pack())],
            [InlineKeyboardButton(text="💾 Сохранить фильтры", callback_data=SubscribeFilterCallback(filter_type="save").pack())],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=SubFilterBackCallback().pack())]
        ]
    )
    
    await bot.send_message(user_id, filter_description, reply_markup=filters_kb)