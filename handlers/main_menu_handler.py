from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from filters import KleinzengenFilter
from aiogram.fsm.context import FSMContext

def register_handlers(dp):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(send_menu, Command("menu"))
    dp.message.register(send_subscriptions_menu, Command("subscriptions"))
    dp.callback_query.register(process_help, lambda c: c.data == "help")

async def send_welcome(message: types.Message, state: FSMContext):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписка на автомобиль", callback_data="subscribe")],
        [InlineKeyboardButton(text="Мои подписки", callback_data="my_subscriptions")],
        [InlineKeyboardButton(text="Найти автомобиль", callback_data="find_car")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
    ])
    await initialize_filter(state)
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=inline_kb)

async def send_menu(message: types.Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписка на автомобиль", callback_data="subscribe")],
        [InlineKeyboardButton(text="Мои подписки", callback_data="my_subscriptions")],
        [InlineKeyboardButton(text="Найти автомобиль", callback_data="find_car")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
    ])
    await message.answer("Меню:", reply_markup=inline_kb)

async def process_help(callback_query: types.CallbackQuery):
    bot = callback_query.bot
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "Это бот для поиска автомобилей.")

async def initialize_filter(state: FSMContext):
    # Создаем новый фильтр и сохраняем его в состоянии
    user_filter = KleinzengenFilter()
    await state.update_data(filter=user_filter)
    
async def send_subscriptions_menu(message: types.Message):
    from handlers.subscriptions_handler import subscriptions
    
    user_id = message.from_user.id
    
    # Проверяем, есть ли активные подписки
    is_subscribed = user_id in subscriptions
    
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оформить подписку", callback_data="subscribe")],
    ])
    
    if is_subscribed:
        # Если пользователь уже подписан, добавляем кнопку отписки
        subscription_info = subscriptions[user_id]
        brand = subscription_info["brand"]
        model = subscription_info["model"]
        
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Изменить подписку", callback_data="subscribe")],
            [InlineKeyboardButton(text="Отписаться", callback_data="unsubscribe")],
        ])
        
        await message.answer(
            f"У вас есть активная подписка на автомобиль {brand} {model}.\n"
            f"Вы будете получать уведомления о новых объявлениях.", 
            reply_markup=inline_kb
        )
    else:
        await message.answer(
            "У вас пока нет активных подписок на автомобили.\n"
            "Подписавшись, вы будете получать уведомления о новых объявлениях.", 
            reply_markup=inline_kb
        )


