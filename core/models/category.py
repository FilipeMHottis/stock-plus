from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome"
    )

    # 💰 Faixas de preço
    price_tier_1 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço (Faixa 1)",
    )
    price_tier_2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço (Faixa 2)",
        blank=True,
        null=True,
    )
    price_tier_3 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço (Faixa 3)",
        blank=True,
        null=True,
    )

    # 📦 Limites de quantidade por faixa
    quantity_limit_1 = models.PositiveIntegerField(
        verbose_name="Limite de quantidade para Faixa 1",
        blank=True,
        null=True,
        help_text="Limite opcional para a primeira faixa de desconto"
    )
    quantity_limit_2 = models.PositiveIntegerField(
        verbose_name="Limite de quantidade para Faixa 2",
        blank=True,
        null=True,
        help_text="Limite opcional para a segunda faixa de desconto"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_price_for_quantity(self, total_quantity: int) -> float:
        """
        Retorna o preço aplicável com base na quantidade total do carrinho.
        - Até quantity_limit_1 → price_tier_1
        - Até quantity_limit_2 → price_tier_2
        - Acima de quantity_limit_2 → price_tier_3
        """
        # ⚙️ Lógica progressiva
        if (
            self.price_tier_3 is not None
            and self.quantity_limit_2
            and total_quantity > self.quantity_limit_2
        ):
            return float(self.price_tier_3)
        elif (
            self.price_tier_2 is not None
            and self.quantity_limit_1
            and total_quantity > self.quantity_limit_1
        ):
            return float(self.price_tier_2)
        else:
            return float(self.price_tier_1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
