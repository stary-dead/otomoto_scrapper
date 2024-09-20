from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,InputMediaPhoto
import asyncio
from concurrent.futures import ThreadPoolExecutor
from utils.brand import Brand
from scrappers import OtomotoScrapper
from callbacks import *
from dotenv import load_dotenv
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from collections import defaultdict
from articles import Article
load_dotenv()
API_TOKEN = os.getenv("BOT_API_TOKEN")  # Замените на свой токен
scrapper = OtomotoScrapper()
subscriptions = defaultdict(lambda: {"brand": None, "model": None})
storage = MemoryStorage()
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
class ArticleState:
    articles: list
    current_index: int

# Главное меню
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Создание главного меню
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписка на автомобиль", callback_data="subscribe")],
        [InlineKeyboardButton(text="Найти автомобиль", callback_data="find_car")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
    ])

    # Отправляем главное меню
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=inline_kb)
@dp.message(Command("menu"))
async def send_welcome(message: types.Message):
    # Создание главного меню
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписка на автомобиль", callback_data="subscribe")],       
        [InlineKeyboardButton(text="Найти автомобиль", callback_data="find_car")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
    ])

    # Отправляем главное меню
    await message.answer("Меню:", reply_markup=inline_kb)



#<------------------------------------------------------------->
@dp.callback_query(lambda c: c.data == "subscribe")
async def process_subscribe(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    # Показываем выбор брендов
    btns = []
    for brand in scrapper.brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=SubscribeBrandCallback(brand=brand).pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Выберите бренд:", reply_markup=inline_kb)

# Обработчик выбора бренда для подписки
@dp.callback_query(SubscribeBrandCallback.filter())
async def process_choose_brand(callback_query: types.CallbackQuery, callback_data: BrandCallback, state: FSMContext):
    brand = callback_data.brand
    await state.update_data(subscribe_brand=brand)

    # Показываем выбор моделей
    models = get_brand_models(brand)
    btns = []
    for model in models:
        btns.append([InlineKeyboardButton(text=model, callback_data=SubscribeModelCallback(model=model, brand=brand).pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Выберите модель:", reply_markup=inline_kb)

# Обработчик выбора модели для подписки
@dp.callback_query(SubscribeModelCallback.filter())
async def process_choose_model(callback_query: types.CallbackQuery, callback_data: SubscribeModelCallback, state: FSMContext):
    model = callback_data.model
    brand = callback_data.brand
    await callback_query.answer()
    # Сохраняем подписку в хранилище
    subscriptions[callback_query.from_user.id] = {"brand": brand, "model": model}
    await bot.send_message(callback_query.from_user.id, f"Вы подписались на {brand} {model}. Обновления будут проверяться каждые 10 минут.")
    
    # Запускаем проверку в фоновом режиме
    asyncio.create_task(check_for_updates(callback_query.from_user.id, brand, model))

# Функция для проверки новых артикулов
async def check_for_updates(user_id, brand_name, model_name):
    brand= scrapper.brands[brand_name]
    brand_id = brand.id
    model_id = brand.models[model_name] if model_name != "all" else None
    old_articles = await asyncio.to_thread(lambda: scrapper.get_articles(brand_id, model_id))
    await asyncio.sleep(10)
    while user_id in subscriptions:
        # Получаем новые артикулы
        new_articles = await asyncio.to_thread(lambda: scrapper.get_articles(brand_id, model_id))

        # Сравниваем с предыдущими
        if new_articles and new_articles != old_articles:
            # Отправляем новые артикулы пользователю
            for article in new_articles:
                if article not in old_articles:
                    await show_article(user_id, article, None)
            old_articles = new_articles

        # Ждем 10 минут перед следующей проверкой
        await asyncio.sleep(60)

# Обработчик для отмены подписки
@dp.callback_query(lambda c: c.data == "unsubscribe")
async def process_unsubscribe(callback_query: types.CallbackQuery):
    if callback_query.from_user.id in subscriptions:
        del subscriptions[callback_query.from_user.id]
        await bot.send_message(callback_query.from_user.id, "Вы отписались от обновлений.")
    else:
        await bot.send_message(callback_query.from_user.id, "Вы не подписаны на обновления.")




# Обработчики для кнопок главного меню
@dp.callback_query(lambda c: c.data == "help")
async def process_help(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "Это бот для поиска автомобилей.")



@dp.callback_query(lambda c: c.data == "find_car")
async def process_find_car(callback_query: types.CallbackQuery):
    await callback_query.answer()
    # После нажатия "Найти автомобиль" показываем бренды
    btns = []
    for brand in scrapper.brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=BrandCallback(brand=brand).pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(callback_query.from_user.id, "Марки авто 🚗:", reply_markup=inline_kb)

# Обработчик нажатия инлайн кнопки
@dp.callback_query(BrandCallback.filter())
async def process_callback_brand_button(callback_query: types.CallbackQuery, callback_data:BrandCallback):
    await callback_query.answer() 
    models = get_brand_models(callback_data.brand)
    btns = []
    if models:
        for model in models:
            btns.append([InlineKeyboardButton(text=model, callback_data=ModelCallback(model=model, brand=callback_data.brand).pack())])
        btns.append([InlineKeyboardButton(text="Все модели", callback_data=ModelCallback(model="all", brand=callback_data.brand).pack())])
        btns.append([InlineKeyboardButton(text="🔙 Назад к брендам", callback_data="back_to_brands")])
        inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)    
        await bot.send_message(callback_query.from_user.id, f"Модельный ряд брэнда {callback_query.data}", reply_markup=inline_kb)

@dp.callback_query(ModelCallback.filter())
async def process_callback_model_button(callback_query: types.CallbackQuery, callback_data: ModelCallback, state: FSMContext):
    brand = scrapper.brands[callback_data.brand]
    stop_event = asyncio.Event()
    loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
    await callback_query.answer()
    try:
        model = brand.models[callback_data.model] if callback_data.model != "all" else None
        articles = await asyncio.to_thread(lambda: scrapper.get_articles(brand.id, model))
        stop_event.set()

        if articles:
            # Сохраняем артикулы в состоянии пользователя
            await state.update_data(articles=articles, current_index=0)
            await show_article(callback_query.from_user.id, articles[0], 0)
    finally:
        await loader_task
async def show_article(user_id: int, article:Article, index:int | None):
    image_url = article.main_image.replace('320x240', '1280x720')
    title = article.title
    subtitle = article.description
    price = article.price
    caption = f"{title}\n\n{subtitle}\n\n{price}"
    
    # Создаем кнопки "Далее" и "Назад"
    btns = []
    if index is not None:
        if index > 0:
            btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
        btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns])
        await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)
    
    else:
        await bot.send_photo(user_id, photo=image_url, caption=caption)

@dp.callback_query(lambda c: c.data == "next_article")
async def next_article(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    articles = data['articles']
    current_index = data['current_index']

    if current_index < len(articles) - 1:
        current_index += 1
    else:
        current_index = 0
    await state.update_data(current_index=current_index)
    await update_article(callback_query.message, articles[current_index], current_index)
    

@dp.callback_query(lambda c: c.data == "prev_article")
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

@dp.callback_query(lambda c: c.data == "back_to_brands")
async def process_callback_back_to_brands(callback_query: types.CallbackQuery):
    await callback_query.answer()
    
    # Создаем клавиатуру с брендами
    btns = []
    for brand in scrapper.brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=BrandCallback(brand=brand).pack())])
        
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)

    # Отправляем сообщение с выбором брендов
    await bot.send_message(callback_query.from_user.id, "Марки авто 🚗:", reply_markup=inline_kb)

async def show_loader(callback_query: types.CallbackQuery, stop_event: asyncio.Event):
    loading_message = await bot.send_message(callback_query.from_user.id, "⏳ Идет подгрузка объявлений с OTOMOTO. Ожидайте... ⏳")
    loader_emojis = ["⏳", "🔄", "⌛", "🔃"]
    
    i = 1
    last_message_text = ""  # Храним последнее сообщение
    while not stop_event.is_set():  # Пока не завершен основной процесс загрузки
        emoji = loader_emojis[i % len(loader_emojis)]  # Меняем эмодзи
        new_message_text = f"{emoji} Идет подгрузка объявлений с OTOMOTO. Ожидайте... {emoji}"

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

def get_brand_models(brand_name: str):
    brand = scrapper.brands.get(brand_name)
    if brand:
        return brand.get_models()
    else:
        return None
if __name__ == '__main__':
    dp.run_polling(bot)
