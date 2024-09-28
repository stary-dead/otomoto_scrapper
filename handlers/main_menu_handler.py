from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def register_handlers(dp):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(send_menu, Command("menu"))
    dp.callback_query.register(process_help, lambda c: c.data == "help")

async def send_welcome(message: types.Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписка на автомобиль", callback_data="subscribe")],
        [InlineKeyboardButton(text="Найти автомобиль", callback_data="find_car")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
    ])
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=inline_kb)

async def send_menu(message: types.Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписка на автомобиль", callback_data="subscribe")],
        [InlineKeyboardButton(text="Найти автомобиль", callback_data="find_car")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
    ])
    await message.answer("Меню:", reply_markup=inline_kb)

async def process_help(callback_query: types.CallbackQuery):
    bot = callback_query.bot
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "Это бот для поиска автомобилей.")
