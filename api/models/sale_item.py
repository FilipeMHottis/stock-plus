from django.db import models
from .sale import Sale
from .product import Product


class SaleItem(models.Model):
    """
    Item de uma venda — associa produto, quantidade e subtotal.
    Agora com cálculo automático de faixa de preço por categoria.
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """
        Salva o item garantindo que o subtotal esteja coerente com o preço unitário.
        """
        self.subtotal = round(float(self.unit_price) * self.quantity, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def get_total_price(self, total_cart_quantity: int) -> float:
        """
        Retorna o total do item considerando a quantidade total do carrinho.
        Usa o método da categoria para determinar o preço correto.
        """
        unit_price = self.product.category.get_price_for_quantity(total_cart_quantity)
        total = round(float(unit_price) * self.quantity, 2)
        return total

    def get_unit_price_for_quantity(self, total_cart_quantity: int) -> float:
        """
        Retorna apenas o preço unitário correto para a quantidade total do carrinho.
        Útil para exibir valores no frontend sem recalcular tudo.
        """
        return self.product.category.get_price_for_quantity(total_cart_quantity)

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"
