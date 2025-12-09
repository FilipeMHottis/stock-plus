from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from .product import Product
from .payment_method import PaymentMethod
from .customer import Customer


class Sale(models.Model):
    """
    Representa uma venda realizada na loja.
    Inclui cliente, vendedor, produtos, método de pagamento, desconto e lucro.
    """

    STATUS_CHOICES = [
        ("completed", "Concluída"),
        ("cancelled", "Cancelada"),
        ("scheduled", "Agendada"),
    ]

    # 📅 Data
    date = models.DateTimeField(default=timezone.now, verbose_name="Data da Venda")

    # 💰 Valores principais
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Valor Total (R$)"
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)], verbose_name="Desconto (R$)"
    )
    paid_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Valor Pago (R$)"
    )
    profit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)], verbose_name="Lucro (R$)"
    )
    total_quantity = models.PositiveIntegerField(default=0)

    # 💳 Método de pagamento
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT,
        related_name="sales", verbose_name="Método de Pagamento"
    )

    # 👤 Cliente
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_DEFAULT,
        default=1, related_name="sales", verbose_name="Cliente"
    )

    # 👨‍💼 Vendedor (usuário logado)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="sales", verbose_name="Vendedor"
    )

    # 📦 Produtos via SaleItem
    products = models.ManyToManyField(Product, through="SaleItem", related_name="sales")

    # 📋 Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="completed",
        verbose_name="Status"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ==================================================
    # MÉTODOS DE NEGÓCIO
    # ==================================================

    def calculate_totals(self):
        """Recalcula total, quantidade total e lucro líquido."""
        items = self.items.all()
        gross_total = sum(float(item.subtotal) for item in items)
        self.total_quantity = sum(item.quantity for item in items)

        # Aplica desconto
        self.total_amount = max(gross_total - float(self.discount or 0), 0)

        # Calcula lucro líquido descontando taxa de operadora
        fee = float(self.payment_method.internal_fee or 0) / 100
        self.profit = round(float(self.total_amount) * (1 - fee), 2)

    def update_items_prices(self):
        """
        Atualiza automaticamente os preços unitários e subtotais
        de acordo com a quantidade total do carrinho.
        """
        items = self.items.all()
        total_qty = sum(item.quantity for item in items)

        for item in items:
            item.unit_price = item.product.category.get_price_for_quantity(total_qty)
            item.save()

        # Recalcula valores gerais
        self.calculate_totals()
        self.save()

    def finalize_sale(self):
        """
        Conclui a venda:
        - Atualiza preços e totais
        - Diminui estoque dos produtos (se for venda imediata)
        """
        from .sale_item import SaleItem  # evita import circular

        self.update_items_prices()

        if self.status == "completed":
            for item in self.items.select_related("product"):
                item.product.stock = max(item.product.stock - item.quantity, 0)
                item.product.save()

    def cancel_sale(self):
        """Cancela a venda e, se necessário, repõe o estoque."""
        if self.status == "completed":
            for item in self.items.select_related("product"):
                item.product.stock += item.quantity
                item.product.save()

        self.status = "cancelled"
        self.save()

    def apply_discount(self, value: float):
        """Aplica um desconto fixo e recalcula totais."""
        self.discount = max(float(value), 0)
        self.calculate_totals()
        self.save()

    def __str__(self):
        return f"Venda #{self.id or 'N/A'} - {self.customer.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ["-date"]
