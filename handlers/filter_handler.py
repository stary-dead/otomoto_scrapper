from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from scrappers import KleinzengenRequestsScrapper, KleinzengenScrapperMock
from articles import Article
from callbacks import BrandCallback, ModelCallback
import asyncio
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from filters import KleinzengenFilter
from .articles_handler import show_loader, show_article, scrapper
import re


class CarFilterState(StatesGroup):
    transmission = State()
    fuel = State()
    price = State()
    mileage = State()
    year = State()
    city = State()

def register_handlers(dp:Dispatcher):
    dp.callback_query.register(show_filters, lambda c: c.data == "show_filters")
    
    dp.callback_query.register(back_to_article, lambda c: c.data == "back_to_article")

    dp.callback_query.register(clear_filters, lambda c: c.data == 'clear_filters')
    dp.callback_query.register(apply_filters, lambda c: c.data == 'list_articles')

    dp.callback_query.register(set_transmission, lambda c: c.data == 'filter_transmission')
    dp.message.register(handle_transmission_input, StateFilter(CarFilterState.transmission))

    dp.message.register(handle_fuel_input, StateFilter(CarFilterState.fuel))
    dp.callback_query.register(set_fuel, lambda c: c.data == 'filter_fuel')

    dp.message.register(handle_price_input, StateFilter(CarFilterState.price))
    dp.callback_query.register(set_price, lambda c: c.data == 'filter_price')

    dp.message.register(handle_year_input, StateFilter(CarFilterState.year))
    dp.callback_query.register(set_year, lambda c: c.data == 'filter_year')

    
    dp.message.register(handle_mileage_input, StateFilter(CarFilterState.mileage))
    dp.callback_query.register(set_mileage, lambda c: c.data == 'filter_mileage')

    dp.message.register(handle_city_input, StateFilter(CarFilterState.city))
    dp.callback_query.register(set_city, lambda c: c.data == 'filter_city')

async def handle_city_input(message:types.Message, state: FSMContext):
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    if user_input in user_filter.CITY_CHOICES.keys():
        user_filter._city = user_input
        await state.update_data(filter=user_filter)  # Сохраняем данные
        
        await message.answer(f"Вы выбрали город: {user_input.capitalize()} ✅", reply_markup=ReplyKeyboardRemove())
        await show_filters_from_message(message=message)
        await state.clear()
        await state.update_data(filter=user_filter)
    else:
        await message.answer("Пожалуйста, выберите из предложенного")

async def set_city(callback_query:types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot
    await callback_query.answer()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    
    keyboard = [[KeyboardButton(text = x)] for x in user_filter.CITY_CHOICES.keys()]
    
    reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    await bot.send_message(callback_query.from_user.id, text="Выберите город.", reply_markup=reply_keyboard)
    await state.set_state(CarFilterState.city)

async def back_to_article(callback_query:types.CallbackQuery):
    callback_query.answer()
    bot = callback_query.bot
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
   
async def handle_year_input(message:types.Message, state: FSMContext):
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    
    if re.match(r'^\d+(:\d+)?$', user_input):
        if len(user_input.split(':'))==2:
                answer = user_input
        else:
            answer = ':'+user_input
        user_filter._year = answer
        await state.update_data(filter=user_filter)  # Сохраняем данные
        
        await message.answer(f"Вы выбрали год: {user_input.capitalize()} ✅", reply_markup=ReplyKeyboardRemove())
        await show_filters_from_message(message=message)
        await state.clear()
        await state.update_data(filter=user_filter)
    else:
        await message.answer("Пожалуйста, введите корректный диапозон")

async def set_year(callback_query:types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot
    await callback_query.answer()

    await bot.send_message(callback_query.from_user.id, text="Введите максимальный год или введите диапозон через двоеточие\nНапример: 2017:2020")
    await state.set_state(CarFilterState.year)


async def handle_mileage_input(message:types.Message, state: FSMContext):
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    
    if re.match(r'^\d+(:\d+)?$', user_input):
        if len(user_input.split(':'))==2:
                answer = user_input
        else:
            answer = ':'+user_input
        user_filter._milleage = answer
        await state.update_data(filter=user_filter)  # Сохраняем данные
        
        await message.answer(f"Вы выбрали пробег: {user_input.capitalize()} км ✅", reply_markup=ReplyKeyboardRemove())
        await show_filters_from_message(message=message)
        await state.clear()
        await state.update_data(filter=user_filter)
    else:
        await message.answer("Пожалуйста, введите корректный диапозон")

async def set_mileage(callback_query:types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot
    await callback_query.answer()

    await bot.send_message(callback_query.from_user.id, text="Введите максимальный пробег или введите диапозон через двоеточие\nНапример: 1000:5000")
    await state.set_state(CarFilterState.mileage)


async def handle_price_input(message:types.Message, state: FSMContext):
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    
    if re.match(r'^\d+(:\d+)?$', user_input):
        if len(user_input.split(':'))==2:
                answer = user_input
        else:
            answer = ':'+user_input
        user_filter._price = answer
        await state.update_data(filter=user_filter)  # Сохраняем данные
        
        await message.answer(f"Вы выбрали цену: {user_input.capitalize()} евро✅", reply_markup=ReplyKeyboardRemove())
        await show_filters_from_message(message=message)
        await state.clear()
        await state.update_data(filter=user_filter)
    else:
        await message.answer("Пожалуйста, введите корректный диапозон")

async def set_price(callback_query:types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot
    await callback_query.answer()

    await bot.send_message(callback_query.from_user.id, text="Введите максимальную цену или введите диапозон через двоеточие\nНапример: 1000:5000")
    await state.set_state(CarFilterState.price)



async def handle_fuel_input(message:types.Message, state: FSMContext):
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    if user_input in user_filter.FUEL_CHOICES.keys():
        user_filter._fuel = user_input
        await state.update_data(filter=user_filter)  # Сохраняем данные
        
        await message.answer(f"Вы выбрали топливо: {user_input.capitalize()} ✅", reply_markup=ReplyKeyboardRemove())
        await show_filters_from_message(message=message)
        await state.clear()
        await state.update_data(filter=user_filter)
    else:
        await message.answer("Пожалуйста, выберите из предложенного")

async def set_fuel(callback_query:types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot
    await callback_query.answer()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    
    keyboard = [[KeyboardButton(text = x)] for x in user_filter.FUEL_CHOICES.keys()]
    
    reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    await bot.send_message(callback_query.from_user.id, text="Выберите тип топлива.", reply_markup=reply_keyboard)
    await state.set_state(CarFilterState.fuel)

async def info(callback_data:types.CallbackQuery):
    print(callback_data.data)

async def set_transmission(callback_query:types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot
    await callback_query.answer()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    
    keyboard = [[KeyboardButton(text = x)] for x in user_filter.TRANSMISSION_CHOICES.keys()]
    
    reply_keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    await bot.send_message(callback_query.from_user.id, text="Выберите тип трансмиссии: Автомат или Механика.", reply_markup=reply_keyboard)
    await state.set_state(CarFilterState.transmission)

    current_state = await state.get_state()
    print(f"Current state in handle_transmission_input: {current_state}")

async def handle_transmission_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    if user_input in user_filter.TRANSMISSION_CHOICES.keys():
        user_filter._transmission = user_input
        await state.update_data(filter=user_filter)  # Сохраняем данные
        
        await message.answer(f"Вы выбрали трансмиссию: {user_input.capitalize()} ✅", reply_markup=ReplyKeyboardRemove())
        await show_filters_from_message(message=message)
        await state.clear()
        await state.update_data(filter=user_filter)
    else:
        await message.answer("Пожалуйста, выберите из предложенного: Автомат или Механика.")

async def clear_filters(callback_query: types.CallbackQuery, state: FSMContext):
    callback_query.answer()
    bot = callback_query.bot
    
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")
    user_filter._city = None
    user_filter._fuel = None
    user_filter._milleage = None
    user_filter._year = None
    user_filter._transmission = None
    user_filter._price = None
    user_filter._page = 1
    await state.update_data(filter=user_filter)
    await bot.send_message(callback_query.from_user.id, text='Фильтры очищены!')
    await show_filters(callback_query=callback_query, state=state)

async def apply_filters(callback_query: types.CallbackQuery, state: FSMContext):
    callback_query.answer()
    bot = callback_query.bot
    stop_event = asyncio.Event()
    loader_task = asyncio.create_task(show_loader(callback_query, stop_event))
    await callback_query.answer()
    
    # Получаем текущий фильтр из состояния
    state_data = await state.get_data()
    user_filter: KleinzengenFilter = state_data.get("filter")

    try:
        print(user_filter)
        # Получаем статьи на основе выбранного бренда и модели
        articles = await asyncio.to_thread(lambda: scrapper.get_articles(user_filter = user_filter))
        stop_event.set()

        if articles:
            # Сохраняем артикулы в состоянии пользователя
            await state.update_data(
                articles=articles,
                current_index=0,
                current_brand_id=user_filter.brand['brand_id'],
                current_model_id=user_filter.brand['model_id'],
                current_page=1
            )
            await show_article(callback_query.from_user.id, articles[0], bot, 0)
    finally:
        await loader_task

async def show_filters(callback_query: types.CallbackQuery, state:FSMContext):
    bot = callback_query.bot
    await callback_query.answer()



    filters_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text = "Фильтр по трансмиссии", callback_data="filter_transmission")],
            [InlineKeyboardButton(text = "Фильтр по топливу", callback_data="filter_fuel")],
            [InlineKeyboardButton(text = "Фильтр по цене", callback_data="filter_price")],
            [InlineKeyboardButton(text = "Фильтр по пробегу", callback_data="filter_mileage")],
            [InlineKeyboardButton(text = "Фильтр по году", callback_data="filter_year")],
            [InlineKeyboardButton(text = "Фильтр по городу", callback_data="filter_city")],
            [InlineKeyboardButton(text = "Очистить", callback_data="clear_filters"),
             InlineKeyboardButton(text = "Перейти к объявлениям",callback_data="list_articles")],
            [InlineKeyboardButton(text = "⬅️ Назад",callback_data="back_to_article")]
        ]
    )

    # Отправляем сообщение с клавиатурой
    await bot.send_message(callback_query.from_user.id, "Выберите фильтры:", reply_markup=filters_kb)

async def show_filters_from_message(message:types.Message):
    filters_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text = "Фильтр по трансмиссии", callback_data="filter_transmission")],
            [InlineKeyboardButton(text = "Фильтр по топливу", callback_data="filter_fuel")],
            [InlineKeyboardButton(text = "Фильтр по цене", callback_data="filter_price")],
            [InlineKeyboardButton(text = "Фильтр по пробегу", callback_data="filter_mileage")],
            [InlineKeyboardButton(text = "Фильтр по году", callback_data="filter_year")],
            [InlineKeyboardButton(text = "Фильтр по городу", callback_data="filter_city")],
            [InlineKeyboardButton(text = "Очистить", callback_data="clear_filters"),
             InlineKeyboardButton(text = "Перейти к объявлениям",callback_data="list_articles")],
            [InlineKeyboardButton(text = "⬅️ Назад",callback_data="back_to_article")]
        ]
    )


    await message.answer("Вы можете настроить следующие фильтры.", reply_markup=filters_kb)