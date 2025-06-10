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
    
# Новые callback-данные для фильтров подписок
class SubscribeFilterCallback(CallbackData, prefix="sub_filter"):
    filter_type:str  # transmission, fuel, price, mileage, year, city
    
class SubFilterBackCallback(CallbackData, prefix="sub_filter_back"):
    pass