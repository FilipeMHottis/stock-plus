from typing import TypedDict, List


class SaleItemDict(TypedDict):
    id: int
    product: str
    quantity: int
    unit_price: float
    subtotal: float


class CustomerDict(TypedDict):
    id: int
    name: str
    trade_name: str
    cnpj_or_cpf: str
    phone: str
    address: str


class SaleDict(TypedDict):
    id: int
    date: str
    customer: CustomerDict
    total_amount: float
    discount: float
    status: str
    payment_method: dict
    items: List[SaleItemDict]


class ChangeDict(TypedDict):
    money_received: float
    change: float
