from aiogram.filters.callback_data import CallbackData

class BrandCallback(CallbackData, prefix="brand"):
    brand:str

class ModelCallback(CallbackData, prefix="model"):
    model:str
    brand:str


class SubscribeBrandCallback(CallbackData, prefix="subscribe_brand"):
    brand:str

class SubscribeModelCallback(CallbackData, prefix="subscribe_model"):
    model:str
    brand:str