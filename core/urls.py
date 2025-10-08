from django.urls import path
from .views.login_view import custom_login_view
from .views.home_view import home
from .views.logout import custom_logout_view
from .views.user_profile_view import user_profile
from .views.customer_views import (
    customer,
    customer_create,
    customer_update,
    customer_delete,
)
from .views.tag_view import (
    tag,
    tag_create,
    tag_update,
    tag_delete,
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
    path(
        "tags/",
        tag,
        name="tag",
    ),
    path(
        "tags/create/",
        tag_create,
        name="tag_create",
    ),
    path(
        "tags/update/<int:id>/",
        tag_update,
        name="tag_update",
    ),
    path(
        "tags/delete/<int:id>/",
        tag_delete,
        name="tag_delete",
    ),
]
