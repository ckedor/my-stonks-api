from enum import IntEnum


class CURRENCY(IntEnum):
    BRL = 1
    USD = 2
    
CURRENCY_MAP = {
    'BRL': CURRENCY.BRL,
    'USD': CURRENCY.USD,
}
