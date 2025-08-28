from django.urls import path
from .views.login import custom_login_view
from .views.home import home
from .views.logout import custom_logout_view

urlpatterns = [
    path("login/", custom_login_view, name="login"),
    path("", home, name="home"),
    path("logout/", custom_logout_view, name="logout"),
]
