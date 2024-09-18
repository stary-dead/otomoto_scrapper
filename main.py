from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from brand import Brand
from scrapper import Scrapper
from callbacks import *
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("BOT_API_TOKEN")  # Замените на свой токен
chrome_driver_path = os.getenv("DRIVER_PATH")
scrapper = Scrapper(chrome_driver_path)
brands = {
    "BMW": Brand("BMW", 'bmw', {
        '1M': '1m', '3GT': '3gt', '5GT': '5gt', '6GT': '6gt', 'i3': 'i3',
        'i4': 'i4', 'i5': 'i5', 'i7': 'i7', 'i8': 'i8', 'Inny': 'ix',
        'iX': 'ix1', 'iX1': 'ix2', 'iX2': 'ix3', 'iX3': 'm2', 'M2': 'm3',
        'M3': 'm4', 'M4': 'm5', 'M5': 'm6', 'M6': 'm8', 'M8': 'other',
        'Seria 1': 'seria-1', 'Seria 2': 'seria-2', 'Seria 3': 'seria-3',
        'Seria 4': 'seria-4', 'Seria 5': 'seria-5', 'Seria 6': 'seria-6',
        'Seria 7': 'seria-7', 'Seria 8': 'seria-8', 'X1': 'x1', 'X2': 'x2',
        'X3': 'x3', 'X3 M': 'x3-m', 'X4': 'x4', 'X4 M': 'x4-m', 'X5': 'x5',
        'X5 M': 'x5-m', 'X6': 'x6', 'X6M': 'x6-m', 'X7': 'x7', 'XM': 'xm',
        'Z1': 'z1', 'Z3': 'z3', 'Z4': 'z4', 'Z4 M': 'z4-m', 'Z8': 'z8'
    }),
    "Audi": Brand("Audi", 'audi', {
        'A1': 'a1', 'A3': 'a3', 'A4': 'a4', 'A5': 'a5', 'A6': 'a6', 'A7': 'a7',
        'A8': 'a8', 'Q2': 'q2', 'Q3': 'q3', 'Q5': 'q5', 'Q7': 'q7', 'Q8': 'q8',
        'TT': 'tt', 'R8': 'r8', 'e-tron': 'etron'
    })

}
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Создание инлайн кнопки
    btns = []
    for brand in brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=BrandCallback(brand=brand).pack())])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)

    # Отправка сообщения с инлайн кнопкой
    await message.answer("Марки авто 🚗:", reply_markup=inline_kb)

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
async def process_callback_model_button(callback_query: types.CallbackQuery, callback_data:ModelCallback):
    brand = brands[callback_data.brand]
    await callback_query.answer()
    if callback_data.model != "all":
        articles = scrapper.get_articles(brand.id, brand.models[callback_data.model])
    else:
        articles = scrapper.get_articles(brand.id)
    if articles:
        for item in articles:
            image_url = item['image'].replace('320x240', '1280x720')
            title = item['title']
            subtitle = item['sub_title']
            price = item['price']
            caption=f"""{title}

    {subtitle}

    {price}"""
            
            await bot.send_photo(callback_query.from_user.id, image_url, caption=caption)
            await asyncio.sleep(1)
        # await bot.send_message(callback_query.from_user.id, f"Brand: {callback_data.brand}, Model: {callback_data.model}")
    

@dp.callback_query(lambda c: c.data == "back_to_brands")
async def process_callback_back_to_brands(callback_query: types.CallbackQuery):
    await callback_query.answer()
    
    # Создаем клавиатуру с брендами
    btns = []
    for brand in brands.keys():
        btns.append([InlineKeyboardButton(text=brand, callback_data=BrandCallback(brand=brand).pack())])
        
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)

    # Отправляем сообщение с выбором брендов
    await bot.send_message(callback_query.from_user.id, "Марки авто 🚗:", reply_markup=inline_kb)

def get_brand_models(brand_name: str):
    brand = brands.get(brand_name)
    if brand:
        return brand.get_models()
    else:
        return None
if __name__ == '__main__':
    dp.run_polling(bot)
