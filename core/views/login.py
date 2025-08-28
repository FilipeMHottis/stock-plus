from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")  # checkbox do "lembrar-me"

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Se NÃO marcar "lembrar-me", a sessão expira ao fechar navegador
            if not remember:
                request.session.set_expiry(0)

            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Usuário ou senha inválidos"})

    return render(request, "login.html")
