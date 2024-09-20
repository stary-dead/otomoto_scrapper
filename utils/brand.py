class Brand:
    def __init__(self, name: str, id: str, models: dict[str, str] = None) -> None:
        self.name = name
        self.id = id
        self.models = models if models else {}

    def get_models(self):
        return list(self.models.keys())

    def get_link(self, chosen_models_names=None):
        link = f"https://www.otomoto.pl/osobowe/{self.id}/"
        if not chosen_models_names:
            return link
        
        model_ids = []
        for name in chosen_models_names:
            model_id = self.models.get(name)
            if model_id:
                model_ids.append(model_id)

        # Присоединяем модели с разделителем
        if model_ids:
            link += "--".join(model_ids)

        return link


brands = {
    "BMW": Brand("BMW", 'bmw', {
        '1M': '1m', '3GT': '3gt', '5GT': '5gt', '6GT': '6gt', 'i3': 'i3',
        'i4': 'i4', 'i5': 'i5', 'i7': 'i7', 'i8': 'i8', 'Inny': 'ix',
        'iX': 'ix1', 'iX1': 'ix2', 'iX2': 'ix3', 'iX3': 'm2', 'M2': 'm3',
        'M3': 'm4', 'M4': 'm5', 'M5': 'm6', 'M6': 'm8', 'M8': 'other',
        'Seria 1': 'seria-1', 'Seria 2': 'seria-2', 'Seria 3': 'seria-3',
        'Seria 4': 'seria-4', 'Seria 5': 'seria-5', 'Seria 6': 'seria-6',
        'Seria 7': 'seria-7', 'Seria 8': 'seria-8', 'X1': 'x1', 'X2': 'x2',
        'X3': 'x3', 'X3 M': 'x3-m', 'X4': 'x4', 'X4 M': 'x4-m', 'X5': 'x5',
        'X5 M': 'x5-m', 'X6': 'x6', 'X6M': 'x6-m', 'X7': 'x7', 'XM': 'xm',
        'Z1': 'z1', 'Z3': 'z3', 'Z4': 'z4', 'Z4 M': 'z4-m', 'Z8': 'z8'
    }),
    "Audi": Brand("Audi", 'audi', {
        'A1': 'a1', 'A3': 'a3', 'A4': 'a4', 'A5': 'a5', 'A6': 'a6', 'A7': 'a7',
        'A8': 'a8', 'Q2': 'q2', 'Q3': 'q3', 'Q5': 'q5', 'Q7': 'q7', 'Q8': 'q8',
        'TT': 'tt', 'R8': 'r8', 'e-tron': 'etron'
    })

}

def get_brand_models(brand_name: str):
    brand = brands.get(brand_name)
    if brand:
        return brand.get_models()
    else:
        return f"Бренд '{brand_name}' не найден."

if __name__ == '__main__':
    brand_name = input("Введите название бренда: ")
    models = get_brand_models(brand_name)
    print(f"Модельный ряд {brand_name}: {models}")
