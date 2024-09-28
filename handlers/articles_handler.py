from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from scrappers import KleinzengenScrapper
from articles import Article
from callbacks import BrandCallback, ModelCallback
import asyncio

scrapper = KleinzengenScrapper()

def register_handlers(dp):
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
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Марки авто 🚗:", reply_markup=inline_kb)


async def next_article(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    articles = data['articles']
    current_index = data['current_index']
    current_page = int(data['current_page'])
    
    if current_index == len(articles) - 1:
        # Загрузить следующую страницу, если текущий индекс - последний в списке
        current_page += 1
        brand_id = data['current_brand_id']
        model_id = data['current_model_id']
        new_articles = await asyncio.to_thread(lambda: scrapper.get_articles(brand_id, model_id, page=current_page))
        
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
    image_url = article.main_image.replace('320x240', '1280x720')
    title = article.title
    subtitle = article.description
    price = article.price
    caption = f"{title}\n\n{subtitle}\n\n{price}"
    
    # Создаем кнопки "Далее" и "Назад"
    btns = []
    if index > 0:
        btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
    btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns])

    # Редактируем сообщение (фото и подпись)
    media = InputMediaPhoto(media=image_url, caption=caption)
    await message.edit_media(media=media, reply_markup=inline_kb)

async def process_callback_brand_button(callback_query: types.CallbackQuery, callback_data:BrandCallback):
    await callback_query.answer() 
    bot = callback_query.bot
    models = get_brand_models(callback_data.brand)
    btns = []
    if models:
        for model in models:
            btns.append([InlineKeyboardButton(text=model, callback_data=ModelCallback(model=model, brand=callback_data.brand).pack())])
        btns.append([InlineKeyboardButton(text="Все модели", callback_data=ModelCallback(model="all", brand=callback_data.brand).pack())])
        btns.append([InlineKeyboardButton(text="🔙 Назад к брендам", callback_data="back_to_brands")])
        inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)    
        await bot.send_message(callback_query.from_user.id, f"Модельный ряд брэнда {callback_query.data}", reply_markup=inline_kb)

async def process_callback_model_button(callback_query: types.CallbackQuery, callback_data: ModelCallback, state: FSMContext):
    brand = scrapper.brands[callback_data.brand]
    bot = callback_query.bot
    stop_event = asyncio.Event()
    loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
    await callback_query.answer()
    try:
        model = brand.models[callback_data.model] if callback_data.model != "all" else None
        articles = await asyncio.to_thread(lambda: scrapper.get_articles(brand.id, model))
        stop_event.set()

        if articles:
            # Сохраняем артикулы в состоянии пользователя
            await state.update_data(articles=articles, current_index=0, current_brand_id=brand.id, current_model_id=model, current_page=1)
            await show_article(callback_query.from_user.id, articles[0], bot, 0)
    finally:
        await loader_task


async def show_article(user_id: int, article:Article, bot,  index:int | None):
    image_url = article.main_image
    title = article.title
    subtitle = article.description
    price = article.price
    caption = f"{title}\n\n{subtitle}\n\n{price}"
    
    btns = []
    try:
        if index is not None:
            if index > 0:
                btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
            btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))

            inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns])
            await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)
        
        else:
            await bot.send_photo(user_id, photo=image_url, caption=caption)
    except:
        print("Ошибка!!!!")
    finally:
        print(image_url)
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