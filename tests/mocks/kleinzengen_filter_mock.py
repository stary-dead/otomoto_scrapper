class KleinzengenFilter:
    def __init__(self, brands=None, min_price=None, max_price=None, min_year=None, max_year=None):
        self.brands = brands or []
        self.min_price = min_price
        self.max_price = max_price
        self.min_year = min_year
        self.max_year = max_year
    
    def apply(self, article):
        """
        Применяет фильтр к статье.
        
        Args:
            article: Объект статьи для фильтрации
            
        Returns:
            bool: True если статья проходит фильтр, False в противном случае
        """
        # Фильтрация по бренду
        if self.brands and article.brand not in self.brands:
            return False
            
        # Фильтрация по цене
        if self.min_price is not None:
            try:
                price = int(article.price)
                if price < self.min_price:
                    return False
            except ValueError:
                pass
                
        if self.max_price is not None:
            try:
                price = int(article.price)
                if price > self.max_price:
                    return False
            except ValueError:
                pass
                
        # Фильтрация по году
        if self.min_year is not None:
            try:
                year = int(article.year)
                if year < self.min_year:
                    return False
            except ValueError:
                pass
                
        if self.max_year is not None:
            try:
                year = int(article.year)
                if year > self.max_year:
                    return False
            except ValueError:
                pass
                
        return True
