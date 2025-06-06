class SubscriptionsHandler:
    def __init__(self):
        self.subscriptions = []
        
    def add_subscription(self, filter_obj):
        """
        Добавляет подписку.
        
        Args:
            filter_obj: Объект фильтра
        """
        self.subscriptions.append(filter_obj)
        
    def remove_subscription(self, index):
        """
        Удаляет подписку по индексу.
        
        Args:
            index: Индекс подписки для удаления
        """
        if 0 <= index < len(self.subscriptions):
            self.subscriptions.pop(index)
            
    def list_subscriptions(self):
        """
        Возвращает список подписок.
        
        Returns:
            list: Список объектов фильтров
        """
        return self.subscriptions
