from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models.category import Category
from ..utils.role_required import role_required
from django.http import HttpRequest


@login_required
def category(request: HttpRequest):
    categories = Category.objects.all()
    return render(
        request,
        "category/category.html",
        {"categories": categories}
    )


@role_required(["admin", "checkout"])
@login_required
def category_create(request: HttpRequest):
    if request.method == "POST":
        name = request.POST.get("name")
        price_tier_1 = request.POST.get("price_tier_1")
        price_tier_2 = request.POST.get("price_tier_2") or None
        price_tier_3 = request.POST.get("price_tier_3") or None
        quantity_limit_1 = request.POST.get("quantity_limit_1") or None
        quantity_limit_2 = request.POST.get("quantity_limit_2") or None

        if not name or not price_tier_1:
            messages.error(
                request,
                "Nome e Preço da Faixa 1 são obrigatórios.",
            )
            return redirect("category")

        Category.objects.create(
            name=name.strip(),
            price_tier_1=price_tier_1,
            price_tier_2=price_tier_2,
            price_tier_3=price_tier_3,
            quantity_limit_1=quantity_limit_1,
            quantity_limit_2=quantity_limit_2,
        )

        messages.success(request, "Categoria criada com sucesso.")
    return redirect("category")


@role_required(["admin", "checkout"])
@login_required
def category_update(request: HttpRequest, category_id: int):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        id = request.POST.get("id")
        name = request.POST.get("name")
        price_tier_1 = request.POST.get("price_tier_1")
        price_tier_2 = request.POST.get("price_tier_2") or None
        price_tier_3 = request.POST.get("price_tier_3") or None
        quantity_limit_1 = request.POST.get("quantity_limit_1") or None
        quantity_limit_2 = request.POST.get("quantity_limit_2") or None

        if not name or not price_tier_1:
            messages.error(
                request,
                "Nome e Preço da Faixa 1 são obrigatórios.",
            )
            return redirect("category")

        if str(category.id) != id:
            messages.error(
                request,
                "ID da categoria inválido.",
            )
            return redirect("category")

        category.name = name.strip()
        category.price_tier_1 = price_tier_1
        category.price_tier_2 = price_tier_2
        category.price_tier_3 = price_tier_3
        category.quantity_limit_1 = quantity_limit_1
        category.quantity_limit_2 = quantity_limit_2
        category.save()

        messages.success(request, "Categoria editada com sucesso.")
    return redirect("category")


@role_required(["admin", "checkout"])
@login_required
def category_delete(request: HttpRequest, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Categoria deletada com sucesso.")
    return redirect("category")
