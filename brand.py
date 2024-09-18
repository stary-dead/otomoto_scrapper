class Brand:
    def __init__(self, name:str, id:str, models:list[dict] = None) -> None:
        self.name = name
        self.id = id
        self.models = []
        if models:
            self.models = models

    def get_link(self, chosed_models_names = None):
        link = f"https://www.otomoto.pl/osobowe/{self.id}/"
        if not chosed_models_names:
            return link
        
        for i, name in enumerate(chosed_models_names):
            last_index = len(chosed_models_names) - 1
            model_id = next((model['id'] for model in self.models if model['name'] == name), None)
            if model_id:

                if i!=last_index:
                    link+=model_id+"--"
                else:
                    link+=model_id
        return link


if __name__ == '__main__':
    bmw = Brand("BMW", 'bmw')
    models = [{'name': '1M', 'id': '1m'}, {'name': '3GT', 'id': '3gt'}, {'name': '5GT', 'id': '5gt'}, {'name': '6GT', 'id': '6gt'}, {'name': 'i3', 'id': 'i3'}, {'name': 'i4', 'id': 'i4'}, {'name': 'i5', 'id': 'i5'}, {'name': 'i7', 'id': 'i7'}, {'name': 'i8', 'id': 'i8'}, {'name': 'Inny', 'id': 'ix'}, {'name': 'iX', 'id': 'ix1'}, {'name': 'iX1', 'id': 'ix2'}, {'name': 'iX2', 'id': 'ix3'}, {'name': 'iX3', 'id': 'm2'}, {'name': 'M2', 'id': 'm3'}, {'name': 'M3', 'id': 'm4'}, {'name': 'M4', 'id': 'm5'}, {'name': 'M5', 'id': 'm6'}, {'name': 'M6', 'id': 'm8'}, {'name': 'M8', 'id': 'other'}, {'name': 'Seria 1', 'id': 'seria-1'}, {'name': 'Seria 2', 'id': 'seria-2'}, {'name': 'Seria 3', 'id': 'seria-3'}, {'name': 'Seria 4', 'id': 'seria-4'}, {'name': 'Seria 5', 'id': 'seria-5'}, {'name': 'Seria 6', 'id': 'seria-6'}, {'name': 'Seria 7', 'id': 'seria-7'}, {'name': 'Seria 8', 'id': 'seria-8'}, {'name': 'X1', 'id': 'x1'}, {'name': 'X2', 'id': 'x2'}, {'name': 'X3', 'id': 'x3'}, {'name': 'X3 M', 'id': 'x3-m'}, {'name': 'X4', 'id': 
'x4'}, {'name': 'X4 M', 'id': 'x4-m'}, {'name': 'X5', 'id': 'x5'}, {'name': 'X5 M', 'id': 'x5-m'}, {'name': 'X6', 'id': 'x6'}, {'name': 'X6M', 'id': 'x6-m'}, {'name': 'X7', 'id': 'x7'}, {'name': 'XM', 'id': 'xm'}, {'name': 'Z1', 'id': 'z1'}, {'name': 'Z3', 'id': 'z3'}, {'name': 'Z4', 'id': 'z4'}, {'name': 'Z4 M', 'id': 'z4-m'}, {'name': 'Z8', 'id': 'z8'}]

    bmw.models = models
    print(bmw.get_link(["1M", "Seria 7"]))