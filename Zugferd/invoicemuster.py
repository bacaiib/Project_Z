from dataclasses import dataclass


@dataclass
class Company:
    name: str
    street: str
    zip_code: str
    city: str

@dataclass
class Rechnungsposition:
    bezeichnung: str
    anzahl: float
    einzelpreis: float
    gesamtpreis: float

@dataclass
class Invoice:
    rechnungsnummer: str
    datum: str
    company: Company
    positions: list[Rechnungsposition]
    zwischensumme: float
    mwst: float
    summe: float

    # def __iter__(self):
    #     return iter(asdict(self).items())