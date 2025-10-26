from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models.product import Product
from ..models.category import Category
from ..models.tag import Tag
from ..utils.role_required import role_required
from django.http import HttpRequest


@login_required
def product(request: HttpRequest):
    products = Product.objects.all()
    categories = Category.objects.all()
    tags = Tag.objects.all()

    return render(
        request,
        "product/product.html",
        {
            "products": products,
            "categories": categories,
            "tags": tags,
        }
    )


@role_required(["admin", "checkout"])
@login_required
def product_update(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        barcode = request.POST.get("barcode")
        category_id = request.POST.get("category")
        tags = request.POST.getlist("tags")

        if not name or not stock:
            messages.error(
                request,
                "Nome e Estoque são obrigatórios.",
            )
            return redirect("product")

        product.name = name
        product.description = description
        product.stock = stock
        product.barcode = barcode
        if image:
            product.upload_image(image)
        product.category_id = category_id
        product.tags.set(tags)
        product.save()

        messages.success(request, "Produto atualizado com sucesso.")
        return redirect("product")


@role_required(["admin", "checkout"])
@login_required
def product_delete(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Produto deletado com sucesso.")
    return redirect("product")


@role_required(["admin", "checkout"])
@login_required
def product_create(request: HttpRequest):
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        barcode = request.POST.get("barcode")
        category_id = request.POST.get("category")
        tags = request.POST.getlist("tags")

        if not name or not stock:
            messages.error(
                request,
                "Nome e Estoque são obrigatórios.",
            )
            return redirect("product")

        product = Product(
            name=name,
            description=description,
            stock=stock,
            barcode=barcode,
            category_id=category_id,
        )
        product.save()

        if image:
            product.upload_image(image)

        if tags:
            product.tags.set(tags)

        messages.success(request, "Produto criado com sucesso.")
        return redirect("product")
