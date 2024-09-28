from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from scrappers import KleinzengenScrapper
from collections import defaultdict
from utils.brand import Brand
from articles import Article
from callbacks import SubscribeBrandCallback, SubscribeModelCallback, BrandCallback
import asyncio

scrapper = KleinzengenScrapper()
subscriptions = defaultdict(lambda: {"brand": None, "model": None})

def register_handlers(dp):
    dp.callback_query.register(process_subscribe, lambda c: c.data == "subscribe")
    dp.callback_query.register(process_choose_brand, SubscribeBrandCallback.filter())
    dp.callback_query.register(process_choose_model, SubscribeModelCallback.filter())
    dp.callback_query.register(process_unsubscribe, lambda c: c.data == "unsubscribe")

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
    if callback_query.from_user.id in subscriptions:
        del subscriptions[callback_query.from_user.id]
        await bot.send_message(callback_query.from_user.id, "Вы отписались от обновлений.")
    else:
        await bot.send_message(callback_query.from_user.id, "Вы не подписаны на обновления.")

async def process_choose_brand(callback_query: types.CallbackQuery, callback_data: BrandCallback, state: FSMContext):
    brand = callback_data.brand
    callback_query.answer()
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
    await callback_query.answer()
    subscriptions[callback_query.from_user.id] = {"brand": brand, "model": model}
    await bot.send_message(callback_query.from_user.id, f"Вы подписались на {brand} {model}. Обновления будут проверяться каждые 10 минут.")
    
    # Запускаем проверку в фоновом режиме
    asyncio.create_task(check_for_updates(bot, callback_query.from_user.id, brand, model))

async def check_for_updates(bot, user_id, brand_name, model_name):
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
                    await show_article(user_id, article, bot, None)
            
            print(old_articles)
            print('\n'*3)
            print(new_articles)
            old_articles = new_articles

        # Ждем 10 минут перед следующей проверкой
        await asyncio.sleep(60)

async def show_article(user_id: int, article:Article, bot,  index:int | None):
    image_url = article.main_image
    title = article.title
    subtitle = article.description
    price = article.price
    caption = f"{title}\n\n{subtitle}\n\n{price}"
    
    btns = []
    if index is not None:
        if index > 0:
            btns.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_article"))
        btns.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next_article"))

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[btns])
        await bot.send_photo(user_id, photo=image_url, caption=caption, reply_markup=inline_kb)
    
    else:
        await bot.send_photo(user_id, photo=image_url, caption=caption)

def get_brand_models(brand_name: str):
    brand = scrapper.brands.get(brand_name)
    if brand:
        return brand.get_models()
    else:
        return None