from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from typing import Any
from django.apps import AppConfig


class Customer(models.Model):
    name = models.CharField(max_length=150, verbose_name="Name")
    trade_name = models.CharField(  # Nome fictício / fantasia
        max_length=150,
        verbose_name="Trade Name",
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
                phone="",
                email=None,
                address=None,
            )
