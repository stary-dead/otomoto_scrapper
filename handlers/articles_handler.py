from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from scrappers import KleinzengenScrapper,KleinzengenScrapperMock
from articles import Article
from callbacks import BrandCallback, ModelCallback
import asyncio
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from filters import KleinzengenFilter

scrapper = KleinzengenScrapper()


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
    data = await state.get_data()
    articles = data['articles']
    current_index = data['current_index']
    
    
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    current_page = user_filter.page
    if current_index == len(articles) - 1:
        # Загрузить следующую страницу, если текущий индекс - последний в списке
        current_page += 1
        new_articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter=user_filter, page=current_page))
        
        if new_articles:
            articles += new_articles
            await state.update_data(articles=articles, current_page=current_page)

    current_index += 1
    if current_index < len(articles):
        await state.update_data(current_index=current_index)
        await update_article(callback_query.message, articles[current_index], current_index)



async def prev_article(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    articles = data['articles']
    current_index = data['current_index']

    if current_index > 0:
        current_index -= 1
        await state.update_data(current_index=current_index)
        await update_article(callback_query.message, articles[current_index], current_index)

async def update_article(message: types.Message, article:Article, index):
    image_url = article.main_image.replace("$_2.AUTO", "$_45.AUTO")
    title = article.title
    subtitle = article.description
    price = article.price
    caption = f"{title}\n\n{subtitle}\n\n{price}"
    link = article.url
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

async def process_callback_brand_button(callback_query: types.CallbackQuery, callback_data:BrandCallback, state: FSMContext):
    await callback_query.answer() 
    bot = callback_query.bot

    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    if not user_filter:
        user_filter = KleinzengenFilter()  # Если фильтр не инициализирован, создаем новый

    # Обновляем бренд в фильтре
    user_filter._brand = {"brand_id": callback_data.brand, "model_id": None}  # Модель пока неизвестна

    await state.update_data(filter=user_filter)
    if callback_data.brand == "all":
        bot = callback_query.bot
        stop_event = asyncio.Event()
        loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
        await callback_query.answer()
        
        try:
            articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter = user_filter))
            stop_event.set()

            if articles:
                # Сохраняем артикулы в состоянии пользователя
                await state.update_data(
                    articles=articles,
                    current_index=0,
                    current_brand_id=None,
                    current_model_id=None,
                    current_page=1
                )
                await show_article(callback_query.from_user.id, articles[0], bot, 0)
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
    bot = callback_query.bot
    stop_event = asyncio.Event()
    loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
    await callback_query.answer()
    
    # Получаем текущий фильтр из состояния
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    if not user_filter:
        user_filter = KleinzengenFilter()  # Если фильтр не инициализирован, создаем новый

    try:
        # Получаем бренд и модель
        brand = scrapper.brands[callback_data.brand]
        model = brand.models[callback_data.model] if callback_data.model != "all" else None
        
        # Обновляем фильтр: сохраняем бренд и модель
        user_filter.brand["model_id"] = callback_data.model if callback_data.model != "all" else "all" 

        
        # Сохраняем обновленный фильтр в состоянии
        await state.update_data(filter=user_filter)
        # Получаем статьи на основе выбранного бренда и модели
        articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter = user_filter))
        stop_event.set()

        if articles:
            # Сохраняем артикулы в состоянии пользователя
            await state.update_data(
                articles=articles,
                current_index=0,
                current_brand_id=brand.id,
                current_model_id=model,
                current_page=1
            )
            await show_article(callback_query.from_user.id, articles[0], bot, 0)
    finally:
        await loader_task



async def show_article(user_id: int, article:Article, bot:Bot,  index:int | None):
    image_url = article.main_image.replace("$_2.AUTO", "$_45.AUTO")
    title = article.title
    subtitle = article.description
    price = article.price
    caption = f"{title}\n\n{subtitle}\n\n{price}"
    link = article.url
    btns = []
    try:
        if index is not None:
            if index > 0:
                btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
            btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))
            link_button = InlineKeyboardButton(text="Открыть на сайте", url=link)
            open_filter_button = InlineKeyboardButton(text="Показать фильтры", callback_data="show_filters")
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns, [link_button], [open_filter_button]])
            await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)
            
        else:
            await bot.send_photo(user_id, photo=image_url, caption=caption)
    except Exception as e:
        print(f"Ошибка!!!! {e}")
    # finally:
    #     print(image_url)

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
    


