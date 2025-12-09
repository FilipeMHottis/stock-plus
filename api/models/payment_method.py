from django.db import models
from django.core.validators import MinValueValidator


class PaymentMethod(models.Model):
    """
    Representa um método de pagamento disponível na loja.
    Suporta diferentes tipos (cash, crédito, débito, pix, etc.)
    e regras de parcelamento, taxas e juros.
    """

    # Tipos de método de pagamento
    TYPE_CHOICES = [
        ("cash", "Dinheiro"),
        ("pix", "PIX"),
        ("debit", "Cartão de Débito"),
        ("credit", "Cartão de Crédito"),
        ("boleto", "Boleto"),
        ("other", "Outro"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Método de Pagamento"
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="cash",
        verbose_name="Tipo de Pagamento"
    )

    # 💸 Taxa interna (para cálculo de lucro líquido)
    internal_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Taxa Interna (%)",
        help_text="Taxa cobrada pela operadora (afeta o lucro da loja)."
    )

    # ⚙️ Campos de parcelamento (válidos apenas para crédito/boleto)
    min_installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Valor Mínimo para Parcelar (R$)",
        blank=True,
        null=True
    )

    max_installments = models.PositiveIntegerField(
        default=1,
        verbose_name="Máximo de Parcelas",
        blank=True,
        null=True
    )

    no_interest_installments = models.PositiveIntegerField(
        default=1,
        verbose_name="Parcelas Sem Juros",
        blank=True,
        null=True
    )

    customer_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Juros ao Cliente (%) ao mês",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -----------------------
    # MÉTODOS DE NEGÓCIO
    # -----------------------

    def clean(self):
        """
        Garante que apenas métodos compatíveis tenham parcelamento.
        """
        from django.core.exceptions import ValidationError

        # Se o tipo for dinheiro, PIX ou débito — bloqueia parcelas
        if self.type in ["cash", "pix", "debit"]:
            if (
                self.max_installments and self.max_installments > 1
            ) or (
                self.customer_interest_rate
                and self.customer_interest_rate > 0
            ):
                raise ValidationError(
                    f"O método '{self.get_type_display()}' "
                    f"não permite parcelamento ou juros."
                )

            # Zera os campos de parcelamento
            self.max_installments = 1
            self.no_interest_installments = 1
            self.customer_interest_rate = 0
            self.min_installment_amount = 0

    def calculate_total_with_interest(
        self,
        amount: float,
        installments: int,
    ) -> float:
        """
        Retorna o valor total considerando juros e número de parcelas.
        Só faz sentido para 'credit' ou 'boleto'.
        """
        if self.type not in ["credit", "boleto"]:
            return float(amount)

        if (
            not self.customer_interest_rate
            or installments <= (self.no_interest_installments or 1)
        ):
            return float(amount)

        monthly_interest = float(self.customer_interest_rate) / 100
        total = amount * (
            (1 + monthly_interest)
            ** (installments - (self.no_interest_installments or 1))
        )
        return round(total, 2)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Método de Pagamento"
        verbose_name_plural = "Métodos de Pagamento"
        ordering = ["name"]
