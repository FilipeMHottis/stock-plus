from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from typing import TypeVar, Optional

UserType = TypeVar("UserType", bound="User")


class CustomUserManager(BaseUserManager["User"]):
    def create_user(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
    ):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(
            username=username, email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
    ):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_active = True
        user.role = "admin"
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("checkout", "Caixa"),
        ("manager", "Gerente"),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="checkout",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    objects = CustomUserManager()

    def __str__(self):
        return self.username
