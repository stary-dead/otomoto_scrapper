from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from handlers import main_menu_handler, subscriptions_handler, articles_handler

load_dotenv()

API_TOKEN = os.getenv("BOT_API_TOKEN")
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Импортируем все обработчики
main_menu_handler.register_handlers(dp)
subscriptions_handler.register_handlers(dp)
articles_handler.register_handlers(dp)

if __name__ == '__main__':
    dp.run_polling(bot)
