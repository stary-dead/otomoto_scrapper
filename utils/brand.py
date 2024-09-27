import json
class Brand:
    def __init__(self, name: str, id: str, models: dict[str, str] = None) -> None:
        self.name = name
        self.id = id
        self.models = models if models else {}

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "models": self.models,
        }
    
    def get_models(self):
        return list(self.models.keys())

class BrandsSerializer:

    @staticmethod
    def serialize(brands):
        brands_dict = {brand_name: brand.to_dict() for brand_name, brand in brands.items()}
        return json.dumps(brands_dict, ensure_ascii=False, indent=4)
    
    @staticmethod
    def deserialize(data:dict):
        brands_dict = json.loads(data)
        brands = {
            brand_name: Brand(brand_data["name"], brand_data["id"], brand_data["models"])
            for brand_name, brand_data in brands_dict.items()
        }
        return brands
