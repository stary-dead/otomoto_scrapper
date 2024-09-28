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
        'Benzin': 'benzin',
        'Diesel': 'diesel',
        'Erdgas (CNG)': 'cng',
        'Autogas (LPG)': 'lpg',
        'Andere Kraftstoffarten': 'andere'
    }

    def __init__(self, 
                 milleage: str | None = None, 
                 year: str | None = None, 
                 fuel: str | None = None, 
                 transmission: str | None = None, 
                 price: str | None = None, 
                 city: str | None = None):
        self._milleage = milleage
        self._year = year
        self._fuel = None
        self._transmission = None
        self._price = price
        self._city = None

        if fuel in self.FUEL_CHOICES:
            self._fuel = self.FUEL_CHOICES[fuel]

        if transmission in self.TRANSMISSION_CHOICES:
            self._transmission = self.TRANSMISSION_CHOICES[transmission]
        
        if city in self.CITY_CHOICES:
            self._city = self.CITY_CHOICES[city]
    
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
