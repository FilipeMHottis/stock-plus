from typing import cast
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest
from ..models.user import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages


@login_required
def user_profile(request: HttpRequest):
    user = cast(User, request.user)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        if username:
            user.username = username
        if email:
            user.email = email

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password:
            if password == confirm_password:
                try:
                    validate_password(password, user)
                    user.set_password(password)
                except ValidationError as e:
                    messages.error(
                        request,
                        "Erro na senha: " + "; ".join(e.messages)
                    )
                    return render(request, "user_profile.html", {
                        "user": user,
                    })

            else:
                messages.error(request, "As senhas não coincidem.")
                return render(request, "user_profile.html", {"user": user})

        user.save()
        return redirect("user_profile")

    return render(request, "user/user_profile.html", {"user": user})
