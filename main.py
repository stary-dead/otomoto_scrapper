from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from brand import Brand

API_TOKEN = '7111658600:AAEvvAUuDl5js9cIxkHg9hvgXYsXDEW8JL8'  # Замените на свой токен
bmw = Brand("BMW", 'bmw')
models = [{'name': '1M', 'id': '1m'}, {'name': '3GT', 'id': '3gt'}, {'name': '5GT', 'id': '5gt'}, {'name': '6GT', 'id': '6gt'}, {'name': 'i3', 'id': 'i3'}, {'name': 'i4', 'id': 'i4'}, {'name': 'i5', 'id': 'i5'}, {'name': 'i7', 'id': 'i7'}, {'name': 'i8', 'id': 'i8'}, {'name': 'Inny', 'id': 'ix'}, {'name': 'iX', 'id': 'ix1'}, {'name': 'iX1', 'id': 'ix2'}, {'name': 'iX2', 'id': 'ix3'}, {'name': 'iX3', 'id': 'm2'}, {'name': 'M2', 'id': 'm3'}, {'name': 'M3', 'id': 'm4'}, {'name': 'M4', 'id': 'm5'}, {'name': 'M5', 'id': 'm6'}, {'name': 'M6', 'id': 'm8'}, {'name': 'M8', 'id': 'other'}, {'name': 'Seria 1', 'id': 'seria-1'}, {'name': 'Seria 2', 'id': 'seria-2'}, {'name': 'Seria 3', 'id': 'seria-3'}, {'name': 'Seria 4', 'id': 'seria-4'}, {'name': 'Seria 5', 'id': 'seria-5'}, {'name': 'Seria 6', 'id': 'seria-6'}, {'name': 'Seria 7', 'id': 'seria-7'}, {'name': 'Seria 8', 'id': 'seria-8'}, {'name': 'X1', 'id': 'x1'}, {'name': 'X2', 'id': 'x2'}, {'name': 'X3', 'id': 'x3'}, {'name': 'X3 M', 'id': 'x3-m'}, {'name': 'X4', 'id': 
'x4'}, {'name': 'X4 M', 'id': 'x4-m'}, {'name': 'X5', 'id': 'x5'}, {'name': 'X5 M', 'id': 'x5-m'}, {'name': 'X6', 'id': 'x6'}, {'name': 'X6M', 'id': 'x6-m'}, {'name': 'X7', 'id': 'x7'}, {'name': 'XM', 'id': 'xm'}, {'name': 'Z1', 'id': 'z1'}, {'name': 'Z3', 'id': 'z3'}, {'name': 'Z4', 'id': 'z4'}, {'name': 'Z4 M', 'id': 'z4-m'}, {'name': 'Z8', 'id': 'z8'}]

bmw.models = models
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Создание инлайн кнопки
    inline_btn = InlineKeyboardButton(text='BMW', callback_data='brand_pressed')
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_btn]])

    # Отправка сообщения с инлайн кнопкой
    await message.answer("Марки авто 🚗:", reply_markup=inline_kb)

# Обработчик нажатия инлайн кнопки
@dp.callback_query(lambda c: c.data == 'brand_pressed')
async def process_callback_brand_button(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Ответ на callback запрос
    btns = []
    for model in bmw.models:
        btns.append([InlineKeyboardButton(text=model['name'], callback_data=model['name'])])
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)    
    await bot.send_message(callback_query.from_user.id, 'Ты нажал на кнопку!', reply_markup=inline_kb)

@dp.callback_query(lambda c: True)
async def process_callback_model_button(callback_query: types.CallbackQuery):
    selected_model = callback_query.data
    await bot.send_message(callback_query.from_user.id, selected_model)
    await callback_query.answer()
if __name__ == '__main__':
    dp.run_polling(bot)
