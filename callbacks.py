from aiogram.filters.callback_data import CallbackData

class BrandCallback(CallbackData, prefix="brand"):
    brand:str

class ModelCallback(CallbackData, prefix="model"):
    model:str
    brand:str
