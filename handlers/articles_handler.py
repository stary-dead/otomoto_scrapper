from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from scrappers import KleinzengenRequestsScrapper, KleinzengenScrapperMock
from articles import Article
from callbacks import BrandCallback, ModelCallback
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from filters import KleinzengenFilter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Используем новый скраппер с requests вместо Selenium
scrapper = KleinzengenRequestsScrapper()


class CarFilterState(StatesGroup):
    transmission = State()
    fuel = State()
    price = State()
    mileage = State()
    year = State()

def register_handlers(dp:Dispatcher):
    dp.callback_query.register(process_find_car, lambda c: c.data == "find_car")
    dp.callback_query.register(next_article, lambda c: c.data == "next_article")
    dp.callback_query.register(prev_article, lambda c: c.data == "prev_article")
    dp.callback_query.register(process_callback_brand_button, BrandCallback.filter())
    dp.callback_query.register(process_callback_model_button, ModelCallback.filter())
    dp.callback_query.register(process_callback_back_to_brands, lambda c: c.data == "back_to_brands")

    

async def process_find_car(callback_query: types.CallbackQuery):
    
    await callback_query.answer()
    bot = callback_query.bot
    # После нажатия "Найти автомобиль" показываем бренды
    btns = []
    for brand in scrapper.brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=BrandCallback(brand=brand).pack())])
    btns.append([InlineKeyboardButton(text="Все модели", callback_data=BrandCallback(brand="all").pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Марки авто 🚗:", reply_markup=inline_kb)


async def next_article(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback_query.from_user.id} запросил следующее объявление")
    data = await state.get_data()
    
    if 'articles' not in data:
        logger.error(f"Ошибка: отсутствует ключ 'articles' в данных состояния для пользователя {callback_query.from_user.id}")
        await callback_query.answer("Пожалуйста, сначала выполните поиск автомобилей")
        return
    
    articles = data['articles']
    current_index = data.get('current_index', 0)
    
    logger.info(f"Текущий индекс: {current_index}, всего объявлений: {len(articles)}")
    
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    
    if not user_filter:
        logger.error(f"Ошибка: отсутствует фильтр для пользователя {callback_query.from_user.id}")
        await callback_query.answer("Ошибка фильтрации. Пожалуйста, начните поиск заново")
        return
        
    current_page = user_filter.page
    
    if current_index == len(articles) - 1:        # Загрузить следующую страницу, если текущий индекс - последний в списке
        current_page += 1
        logger.info(f"Загрузка следующей страницы {current_page} для пользователя {callback_query.from_user.id}")
        try:
            new_articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter=user_filter, page=current_page))
            
            # new_articles всегда будет списком (пустым в случае ошибки)
            if new_articles and len(new_articles) > 0:
                logger.info(f"Получено {len(new_articles)} новых объявлений со страницы {current_page}")
                
                # Проверка на дубликаты по URL
                existing_urls = {article.url for article in articles}
                unique_new_articles = [article for article in new_articles if article.url not in existing_urls]
                
                logger.info(f"Отфильтровано {len(new_articles) - len(unique_new_articles)} дубликатов, добавлено {len(unique_new_articles)} уникальных объявлений")
                
                articles += unique_new_articles
                await state.update_data(articles=articles, current_page=current_page)
            else:
                logger.info(f"Достигнут конец списка объявлений для пользователя {callback_query.from_user.id}")
                await callback_query.answer("Больше объявлений нет")
        except Exception as e:
            logger.error(f"Ошибка при загрузке новых объявлений: {e}")
            await callback_query.answer("Произошла ошибка при загрузке новых объявлений")
            return

    current_index += 1
    if current_index < len(articles):
        logger.info(f"Показываю объявление {current_index+1}/{len(articles)} для пользователя {callback_query.from_user.id}")
        await state.update_data(current_index=current_index)
        await update_article(callback_query.message, articles[current_index], current_index)
    else:
        logger.info(f"Достигнут конец списка объявлений для пользователя {callback_query.from_user.id}")
        await callback_query.answer("Больше объявлений нет")



async def prev_article(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback_query.from_user.id} запросил предыдущее объявление")
    data = await state.get_data()
    
    if 'articles' not in data:
        logger.error(f"Ошибка: отсутствует ключ 'articles' в данных состояния для пользователя {callback_query.from_user.id}")
        await callback_query.answer("Пожалуйста, сначала выполните поиск автомобилей")
        return
    
    articles = data['articles']
    current_index = data.get('current_index', 0)
    
    logger.info(f"Текущий индекс: {current_index}, всего объявлений: {len(articles)}")

    if current_index > 0:
        current_index -= 1
        logger.info(f"Показываю объявление {current_index+1}/{len(articles)} для пользователя {callback_query.from_user.id}")
        await state.update_data(current_index=current_index)
        await update_article(callback_query.message, articles[current_index], current_index)
    else:
        logger.info(f"Достигнуто начало списка объявлений для пользователя {callback_query.from_user.id}")
        await callback_query.answer("Это первое объявление")

async def update_article(message: types.Message, article:Article, index):
    try:
        image_url = article.main_image.replace("$_2.AUTO", "$_45.AUTO")
        title = article.title
        subtitle = article.description
        price = article.price
        caption = f"{title}\n\n{subtitle}\n\n{price}"
        link = article.url
        
        # Используем URL вместо ID для идентификации объявления
        logger.info(f"Обновление объявления: URL={link}")
        
        # Создаем кнопки "Далее" и "Назад"
        btns = []
        if index > 0:
            btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
        btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))
        open_filter_button = InlineKeyboardButton(text="Показать фильтры", callback_data="show_filters")
        link_button = InlineKeyboardButton(text="Открыть на сайте", url=link)
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns, [link_button], [open_filter_button]]) if link_button else InlineKeyboardMarkup(inline_keyboard=[btns, [open_filter_button]])

        # Редактируем сообщение (фото и подпись)
        media = InputMediaPhoto(media=image_url, caption=caption)
        await message.edit_media(media=media, reply_markup=inline_kb)
        logger.info(f"Объявление успешно обновлено (индекс: {index})")
    except Exception as e:
        logger.error(f"Ошибка при обновлении объявления: {e}")
        # В случае ошибки пробуем отправить сообщение об ошибке
        try:
            await message.edit_text("Произошла ошибка при загрузке объявления. Попробуйте снова.")
        except:
            logger.error("Не удалось отправить сообщение об ошибке")

async def process_callback_brand_button(callback_query: types.CallbackQuery, callback_data:BrandCallback, state: FSMContext):
    logger.info(f"Пользователь {callback_query.from_user.id} выбрал бренд {callback_data.brand}")
    await callback_query.answer() 
    bot = callback_query.bot

    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    if not user_filter:
        logger.info(f"Создание нового фильтра для пользователя {callback_query.from_user.id}")
        user_filter = KleinzengenFilter()  # Если фильтр не инициализирован, создаем новый

    # Обновляем бренд в фильтре
    logger.info(f"Установка бренда {callback_data.brand} в фильтр")
    user_filter._brand = {"brand_id": callback_data.brand, "model_id": None}  # Модель пока неизвестна

    await state.update_data(filter=user_filter)
    if callback_data.brand == "all":
        logger.info(f"Пользователь {callback_query.from_user.id} выбрал опцию 'Все модели'")
        bot = callback_query.bot
        stop_event = asyncio.Event()
        loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
        await callback_query.answer()
        
        try:            
            logger.info(f"Запрос всех объявлений для пользователя {callback_query.from_user.id}")
            articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter=user_filter))
            stop_event.set()
            
            # articles теперь всегда будет списком (пустым в случае ошибки)
            logger.info(f"Получено {len(articles)} объявлений")

            if articles and len(articles) > 0:
                # Логируем ID объявлений для отладки            # Используем URL вместо ID для отслеживания объявлений
                article_urls = [article.url for article in articles[:5]]
                logger.info(f"Первые 5 объявлений с URL: {article_urls}")
                
                # Сохраняем артикулы в состоянии пользователя
                await state.update_data(
                    articles=articles,
                    current_index=0,
                    current_brand_id=None,
                    current_model_id=None,
                    current_page=1
                )
                await show_article(callback_query.from_user.id, articles[0], bot, 0)
            else:
                logger.warning(f"Не найдено объявлений для пользователя {callback_query.from_user.id}")
                await bot.send_message(callback_query.from_user.id, "По вашему запросу не найдено объявлений. Попробуйте изменить параметры поиска.")
        except Exception as e:
            logger.error(f"Ошибка при обработке 'all': {e}")
            await bot.send_message(callback_query.from_user.id, "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте снова.")
        finally:
            await loader_task
        return
    # Генерация кнопок для моделей бренда
    models = get_brand_models(callback_data.brand)
    btns = []
    if models:
        for model in models:
            btns.append([InlineKeyboardButton(
                text=model,
                callback_data=ModelCallback(model=model, brand=callback_data.brand).pack()
            )])
        btns.append([InlineKeyboardButton(text="Все модели", callback_data=ModelCallback(model="all", brand=callback_data.brand).pack())])
        btns.append([InlineKeyboardButton(text="🔙 Назад к брендам", callback_data="back_to_brands")])
    
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, f"Модельный ряд бренда {callback_data.brand}", reply_markup=inline_kb)
    
async def process_callback_model_button(callback_query: types.CallbackQuery, callback_data: ModelCallback, state: FSMContext):
    logger.info(f"Пользователь {callback_query.from_user.id} выбрал модель {callback_data.model} бренда {callback_data.brand}")
    bot = callback_query.bot
    stop_event = asyncio.Event()
    loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
    await callback_query.answer()
    
    # Получаем текущий фильтр из состояния
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    if not user_filter:
        logger.info(f"Создание нового фильтра для пользователя {callback_query.from_user.id}")
        user_filter = KleinzengenFilter()  # Если фильтр не инициализирован, создаем новый

    try:
        # Получаем бренд и модель
        brand = scrapper.brands[callback_data.brand]
        model = brand.models[callback_data.model] if callback_data.model != "all" else None
        
        logger.info(f"Настройка фильтра: бренд={callback_data.brand}, модель={callback_data.model}")
        # Обновляем фильтр: сохраняем бренд и модель
        user_filter.brand["model_id"] = callback_data.model if callback_data.model != "all" else "all" 
        
        # Сохраняем обновленный фильтр в состоянии
        await state.update_data(filter=user_filter)
          # Получаем статьи на основе выбранного бренда и модели
        logger.info(f"Запрос объявлений для фильтра: {user_filter}")
        try:
            articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter=user_filter))
            # articles всегда будет списком (пустым в случае ошибки)
            logger.info(f"Получено {len(articles)} объявлений")
        except Exception as e:
            logger.error(f"Ошибка при запросе объявлений: {e}")
            articles = []
            
        stop_event.set()

        if articles and len(articles) > 0:
            # Сохраняем артикулы в состоянии пользователя
            # Логируем ID объявлений для отладки            # Используем URL вместо ID для отслеживания объявлений
            article_urls = [article.url for article in articles[:5]]
            logger.info(f"Сохранение первых 5 объявлений с URL: {article_urls}")
            
            await state.update_data(
                articles=articles,
                current_index=0,
                current_brand_id=brand.id,
                current_model_id=model,
                current_page=1
            )
            await show_article(callback_query.from_user.id, articles[0], bot, 0)
        else:
            logger.warning(f"Не найдено объявлений для пользователя {callback_query.from_user.id}")
            await bot.send_message(callback_query.from_user.id, "По вашему запросу не найдено объявлений. Попробуйте изменить параметры поиска.")
    except Exception as e:
        logger.error(f"Ошибка в process_callback_model_button: {e}")
        await bot.send_message(callback_query.from_user.id, "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте снова.")
    finally:
        await loader_task



async def show_article(user_id: int, article:Article, bot:Bot, index:int | None):
    logger.info(f"Показ объявления для пользователя {user_id}, индекс: {index}")
    try:
        image_url = article.main_image.replace("$_2.AUTO", "$_45.AUTO")
        title = article.title
        subtitle = article.description
        price = article.price
        
        caption = f"{title}\n\n{subtitle}\n\n{price}"
        link = article.url
        
        # Используем URL для идентификации объявления вместо ID
        logger.info(f"Данные объявления: URL={link}")
        
        btns = []
        if index is not None:
            if index > 0:
                btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
            btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))
            link_button = InlineKeyboardButton(text="Открыть на сайте", url=link)
            open_filter_button = InlineKeyboardButton(text="Показать фильтры", callback_data="show_filters")
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns, [link_button], [open_filter_button]])
            await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)
            logger.info(f"Объявление успешно отправлено с индексом {index}")
        else:
            await bot.send_photo(user_id, photo=image_url, caption=caption)
            logger.info("Объявление успешно отправлено без индекса")
    except Exception as e:
        logger.error(f"Ошибка при показе объявления: {e}")
        try:
            await bot.send_message(user_id, f"Произошла ошибка при загрузке объявления: {e}")
        except:
            logger.error(f"Не удалось отправить сообщение об ошибке пользователю {user_id}")

async def show_loader(callback_query: types.CallbackQuery, stop_event: asyncio.Event):
    bot = callback_query.bot
    loading_message = await bot.send_message(callback_query.from_user.id, f"⏳ Идет подгрузка объявлений с {scrapper}. Ожидайте... ⏳")
    loader_emojis = ["⏳", "🔄", "⌛", "🔃"]
    
    i = 1
    last_message_text = ""  # Храним последнее сообщение
    while not stop_event.is_set():  # Пока не завершен основной процесс загрузки
        emoji = loader_emojis[i % len(loader_emojis)]  # Меняем эмодзи
        new_message_text = f"{emoji} Идет подгрузка объявлений с {scrapper}. Ожидайте... {emoji}"

        if new_message_text != last_message_text:  # Проверяем, изменился ли текст
            await bot.edit_message_text(new_message_text, 
                                        chat_id=loading_message.chat.id, 
                                        message_id=loading_message.message_id)
            last_message_text = new_message_text  # Обновляем последнее сообщение
        
        await asyncio.sleep(1)  # Задержка в 1 секунду
        i += 1

    # После завершения загрузки удаляем сообщение
    await bot.delete_message(chat_id=loading_message.chat.id, message_id=loading_message.message_id)
    await callback_query.answer()

async def process_callback_back_to_brands(callback_query: types.CallbackQuery):
    bot = callback_query.bot
    await callback_query.answer()
    
    # Создаем клавиатуру с брендами
    btns = []
    for brand in scrapper.brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=BrandCallback(brand=brand).pack())])
        
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)

    # Отправляем сообщение с выбором брендов
    await bot.send_message(callback_query.from_user.id, "Марки авто 🚗:", reply_markup=inline_kb)

def get_brand_models(brand_name: str):
    brand = scrapper.brands.get(brand_name)
    if brand:
        return brand.get_models()
    else:
        return None



