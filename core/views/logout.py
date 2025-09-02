from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpRequest


def custom_logout_view(request: HttpRequest):
    logout(request)
    return redirect("login")
