from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request: HttpRequest):
    return render(request, "home.html", {"user": request.user})
