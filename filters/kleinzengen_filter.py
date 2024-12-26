class KleinzengenFilter:
    TRANSMISSION_CHOICES = {
        'Автомат': 'autos.shift_s:automatik',
        'Механика': 'autos.shift_s:manuell'
    }

    CITY_CHOICES = {
        'Baden-Württemberg': '7970',
        'Bayern': '5510',
        'Berlin': '3331',
        'Brandenburg': '7711',
        'Bremen': '1',
        'Hamburg': '9409',
        'Hessen': '4279',
        'Mecklenburg-Vorpommern': '61',
        'Niedersachsen': '2428',
        'Nordrhein-Westfalen': '928',
        'Rheinland-Pfalz': '4938',
        'Saarland': '285',
        'Sachsen': '3799',
        'Sachsen-Anhalt': '2165',
        'Schleswig-Holstein': '408',
        'Thüringen': '3548'
    }

    FUEL_CHOICES = {
        'Benzin': 'autos.fuel_s:benzin',
        'Diesel': 'autos.fuel_s:diesel',
        'Erdgas (CNG)': 'autos.fuel_s:cng',
        'Autogas (LPG)': 'autos.fuel_s:lpg',
        'Andere Kraftstoffarten': 'autos.fuel_s:andere'
    }

    def __init__(self, 
                 brand:dict | None=None,
                 milleage: str | None = None, 
                 year: str | None = None,
                 fuel: str | None = None, 
                 transmission: str | None = None, 
                 price: str | None = None, 
                 city: str | None = None,
                 page:int = 1):
        self._brand = brand
        self._milleage = milleage
        self._year = year
        self._fuel = None
        self._transmission = None
        self._price = None
        self._city = None
        self._page = page

        if fuel in self.FUEL_CHOICES:
            self._fuel = self.FUEL_CHOICES[fuel]

        if transmission in self.TRANSMISSION_CHOICES:
            self._transmission = self.TRANSMISSION_CHOICES[transmission]
        
        if city in self.CITY_CHOICES:
            self._city = city
    @property
    def get_web_url(self)->str:
        brand_id = self.brand['brand_id'] if self.brand != "all" else None
        url = "https://www.kleinanzeigen.de/s-autos/"
        year = None
        if brand_id:
            url+=brand_id+"/"
            brand_id = "autos.marke_s:"+brand_id
        city_code = self.CITY_CHOICES[self.city] if self.city else None

        if self.city:
            url+=self.city.lower()+"/"

        if self.price:
            url+=f"preis:{self.price}/"
        if self.year:
            years = self.year.replace(':', "%2C")
            year = f"autos.ez_i:{years}"
        url+=f"seite:{self.page}/"
        # self.page = page

        url+=f"c216l{city_code}" if self.city else "c216"
        model_id = f"autos.model_s:{self.brand['model_id']}" if self.brand and self.brand['model_id'] != "all" else None
        url="+".join([x for x in [url,brand_id, self.transmission, model_id, year] if x!= None])

        return url
        
    @property
    def page(self) -> int:
        return self._page
    
    @property
    def brand(self) -> dict | None:
        return self._brand
    @property
    def milleage(self) -> str | None:
        return self._milleage

    @property
    def year(self) -> str | None:
        return self._year

    @property
    def fuel(self) -> str | None:
        return self._fuel

    @property
    def transmission(self) -> str | None:
        return self._transmission

    @property
    def price(self) -> str | None:
        return self._price

    @property
    def city(self) -> str | None:
        return self._city
    
    def __str__(self):
        return (
            f"Brand: {self.brand}, "
            f"Mileage: {self.milleage}, "
            f"Year: {self.year}, "
            f"Fuel: {self.fuel}, "
            f"Transmission: {self.transmission}, "
            f"Price: {self.price}, "
            f"City: {self.city}, "
            f"Page: {self.page}"
        )
import asyncio
if __name__ == "__main__":
    filters = KleinzengenFilter(brand={"brand_id":"bmw", "model_id":"5er"},
                                fuel="Diesel",transmission="Автомат", price="1000-5000", city='Berlin')
    
    print(filters.get_web_url)