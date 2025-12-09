from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from typing import Any
from django.apps import AppConfig
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity


class Customer(models.Model):
    name = models.CharField(max_length=150, verbose_name="Name")
    trade_name = models.CharField(  # Nome fictício / fantasia
        max_length=150,
        verbose_name="Trade Name",
        blank=True,
        null=True
    )
    cnpj_or_cpf = models.CharField(  # Cadastro Nacional da Pessoa Jurídica ou Cadastro de Pessoas Físicas
        max_length=20,
        verbose_name="CNPJ or CPF",
        blank=True,
        null=True
    )
    phone = models.CharField(max_length=20, verbose_name="Phone")
    email = models.EmailField(
        verbose_name="Email",
        blank=True,
        null=True
    )
    address = models.TextField(
        verbose_name="Address",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.trade_name or self.name

    @staticmethod
    def search_customers(query: str):
        """Busca clientes pelo nome, nome fantasia, CNPJ/CPF, telefone ou id."""
        if not query:
            return Customer.objects.all()

        # busca se for id exato
        if query.isdigit():
            customer_by_id = Customer.objects.filter(id=int(query))
            if customer_by_id.exists():
                return customer_by_id

        # Busca com trigramas
        customers = (
            Customer.objects.annotate(
                similarity=(
                    TrigramSimilarity('name', query) +
                    TrigramSimilarity('trade_name', query) +
                    TrigramSimilarity('cnpj_or_cpf', query) +
                    TrigramSimilarity('phone', query)
                )
            )
            .filter(
                Q(similarity_name__gt=0.3) |
                Q(similarity_trade_name__gt=0.3) |
                Q(similarity_cnpj_or_cpf__gt=0.3) |
                Q(similarity_phone__gt=0.3) |
                Q(id__iexact=query)
            )
            .order_by('-similarity')
        )

        return customers

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


@receiver(post_migrate)
def create_default_customer(sender: AppConfig, **kwargs: Any) -> None:
    if sender.name == "core":
        if not Customer.objects.exists():
            Customer.objects.create(
                name="Cliente Avulso",
                trade_name=None,
                cnpj_or_cpf=None,
                phone="",
                email=None,
                address=None,
            )
