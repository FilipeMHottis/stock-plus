from django.urls import path
from .views.login_view import custom_login_view
from .views.home_view import home
from .views.logout import custom_logout_view
from .views.user_profile_view import user_profile
from django.conf import settings
from django.conf.urls.static import static
from .views.customer_view import (
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
from .views.category_view import (
    category,
    category_create,
    category_update,
    category_delete,
)
from .views.product_view import (
    product,
    product_create,
    product_update,
    product_delete,
    search_products
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
    path(
        "categories/",
        category,
        name="category",
    ),
    path(
        "categories/create/",
        category_create,
        name="category_create",
    ),
    path(
        "categories/update/<int:category_id>/",
        category_update,
        name="category_update",
    ),
    path(
        "categories/delete/<int:category_id>/",
        category_delete,
        name="category_delete",
    ),
    path(
        "products/",
        product,
        name="product",
    ),
    path(
        "products/create/",
        product_create,
        name="product_create",
    ),
    path(
        "products/update/<int:product_id>/",
        product_update,
        name="product_update",
    ),
    path(
        "products/delete/<int:product_id>/",
        product_delete,
        name="product_delete",
    ),
    path(
        "products/search/",
        search_products,
        name="search_products",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
