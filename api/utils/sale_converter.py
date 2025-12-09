from ..types.sales_types import SaleDict, SaleItemDict, CustomerDict


def sale_to_dict(sale) -> SaleDict:
    customer = sale.customer

    customer_dict: CustomerDict = {
        "id": customer.id,
        "name": customer.name,
        "trade_name": customer.trade_name,
        "cnpj_or_cpf": customer.cnpj_or_cpf,
        "phone": customer.phone,
        "address": customer.address,
    }

    items_list: list[SaleItemDict] = []

    for item in sale.items.all():
        items_list.append({
            "id": item.id,
            "product": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "subtotal": float(item.subtotal),
        })

    return {
        "id": sale.id,
        "date": sale.date.strftime("%Y-%m-%d %H:%M:%S"),
        "customer": customer_dict,
        "total_amount": float(sale.total_amount),
        "discount": float(sale.discount),
        "status": sale.status,
        "payment_method": sale.payment_method.name,
        "items": items_list,
    }
