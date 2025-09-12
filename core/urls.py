from django.urls import path
from .views.login import custom_login_view
from .views.home import home
from .views.logout import custom_logout_view
from .views.user_profile import user_profile
from .views.customer_views import (
    customer,
    customer_create,
    customer_update,
    customer_delete,
)

urlpatterns = [
    path(
        "login/",
        custom_login_view,
        name="login",
    ),
    path(
        "",
        home,
        name="home",
    ),
    path(
        "logout/",
        custom_logout_view,
        name="logout",
    ),
    path(
        "user/",
        user_profile,
        name="user_profile",
    ),
    path(
        "customers/",
        customer,
        name="customer",
    ),
    path(
        "customers/create/",
        customer_create,
        name="customer_create",
    ),
    path(
        "customers/update/<int:id>/",
        customer_update,
        name="customer_update",
    ),
    path(
        "customers/delete/<int:id>/",
        customer_delete,
        name="customer_delete",
    ),
]
