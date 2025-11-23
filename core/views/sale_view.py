import json
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from ..models import Sale, SaleItem, Product, Customer, PaymentMethod
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.urls import reverse


# =====================================================
# BUSCA DE PRODUTOS PARA VENDA AJAX
# ====================================================
@login_required
def search_products_sale(request):
    query = request.GET.get("q", "").strip()
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 10))

    # Busca
    if query:
        products = Product.search_products(query)
    else:
        products = Product.objects.all().order_by("name")

    # Paginação
    paginator = Paginator(products, per_page)
    page_obj = paginator.get_page(page)

    # Renderiza o HTML atualizado
    html = render_to_string(
        "sale/partials/product_list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "page_sizes": [5, 10, 20, 50],
        },
        request=request
    )

    return JsonResponse({"success": True, "html": html})


# =====================================================
# 1️⃣ LISTAGEM / PÁGINA DE VENDA
# =====================================================
@login_required
def sale(request):
    """Exibe a página de criação de uma nova venda (frontend)."""

    # ordena produtos por nome e traz categoria relacionada
    products = Product.objects.select_related("category").all().order_by("name")

    # Ordernar para que produtos com estoque zero apareçam por último
    products = sorted(products, key=lambda p: p.stock == 0)

    # Paginação inicial
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 10))
    paginator = Paginator(products, per_page)
    page_obj = paginator.get_page(page)

    customers = Customer.objects.all()
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    page_sizes = [5, 10, 20, 50]

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "customers": customers,
        "payment_methods": payment_methods,
        "page_sizes": page_sizes,
    }
    return render(request, "sale/sale.html", context)


# =====================================================
# 2️⃣ VISUALIZAÇÃO PRÉVIA DE VENDA (AJAX)
# =====================================================
@login_required
def sale_preview(request):
    """
    Calcula o preço total e unitário de uma venda antes de finalizá-la.
    Retorna preços com base nas faixas de categoria.
    """
    try:
        data = json.loads(request.body)
        items = data.get("items", [])
        discount = float(data.get("discount", 0))

        # Calcula quantidade total
        total_quantity = sum(int(item.get("quantity", 0)) for item in items)
        total = 0
        item_details = []

        for item in items:
            product_id = int(item.get("product_id"))
            quantity = int(item.get("quantity", 0))

            product = Product.objects.select_related("category").get(id=product_id)
            category = product.category

            unit_price = category.get_price_for_quantity(total_quantity)
            subtotal = round(unit_price * quantity, 2)

            total += subtotal
            item_details.append({
                "product_id": product.id,
                "product": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        total_after_discount = max(total - discount, 0)

        return JsonResponse({
            "success": True,
            "total_quantity": total_quantity,
            "total": round(total_after_discount, 2),
            "discount": discount,
            "items": item_details
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# =====================================================
# 3️⃣ CRIAÇÃO DE VENDA
# =====================================================
@login_required
@transaction.atomic
def sale_create(request):
    """
    Cria uma nova venda.
    Aceita:
    - JSON via fetch (AJAX)
    - POST tradicional HTML
    """

    # ---------------------------------------------------
    # 1) Verificar se a requisição vem via AJAX/JSON
    # ---------------------------------------------------
    is_json = request.headers.get("Content-Type") == "application/json"

    if is_json:
        try:
            data = json.loads(request.body)

            customer_id = data.get("customer")
            payment_id = data.get("payment_method")
            discount = Decimal(str(data.get("discount") or 0))
            status = data.get("status", "completed")
            scheduled_date = data.get("scheduled_date")
            items = data.get("items", [])

        except Exception as e:
            return JsonResponse({"success": False, "error": f"JSON inválido: {e}"})
    else:
        # FORM normal (não AJAX)
        customer_id = request.POST.get("customer")
        payment_id = request.POST.get("payment_method")
        discount = Decimal(request.POST.get("discount") or 0)
        status = request.POST.get("status", "completed")
        scheduled_date = request.POST.get("scheduled_date")

        # Lê itens do formulário
        items = []
        for key, value in request.POST.items():
            if key.startswith("product_"):
                items.append({
                    "product_id": int(key.split("_")[1]),
                    "quantity": int(value)
                })

    # ---------------------------------------------------
    # 2) Validar dados principais
    # ---------------------------------------------------
    if not items:
        if is_json:
            return JsonResponse({"success": False, "error": "Carrinho vazio."})
        messages.error(request, "Adicione pelo menos um produto.")
        return redirect("sale")

    customer = get_object_or_404(Customer, id=customer_id)
    payment_method = get_object_or_404(PaymentMethod, id=payment_id)

    total_quantity = 0
    total_amount = Decimal("0.00")
    cart = []

    # ---------------------------------------------------
    # 3) Montar itens e calcular totais
    # ---------------------------------------------------
    for item in items:
        product_id = int(item["product_id"])
        quantity = int(item["quantity"])

        if quantity <= 0:
            continue

        product = get_object_or_404(Product, id=product_id)
        total_quantity += quantity

        # preço baseado no total geral da venda (tabela de categoria)
        unit_price = Decimal(product.category.get_price_for_quantity(total_quantity))
        subtotal = unit_price * quantity
        total_amount += subtotal

        cart.append({
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    # ---------------------------------------------------
    # 4) Aplicar desconto e calcular lucro
    # ---------------------------------------------------
    total_amount -= discount
    total_amount = max(total_amount, Decimal("0.00"))

    fee = Decimal(payment_method.internal_fee or 0) / 100
    profit = total_amount * (1 - fee)

    # ---------------------------------------------------
    # 5) Criar a venda
    # ---------------------------------------------------
    sale = Sale.objects.create(
        customer=customer,
        payment_method=payment_method,
        total_amount=total_amount,
        discount=discount,
        paid_amount=total_amount,
        profit=profit,
        total_quantity=total_quantity,
        seller=request.user,
        status=status,
        date=timezone.now() if status == "completed" else scheduled_date,
    )

    # Criar itens + baixar estoque
    for item in cart:
        SaleItem.objects.create(
            sale=sale,
            product=item["product"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            subtotal=item["subtotal"],
        )

        if status == "completed":
            item["product"].stock -= item["quantity"]
            item["product"].save()

    # ---------------------------------------------------
    # 6) Resposta AJAX JSON
    # ---------------------------------------------------
    if is_json:
        return JsonResponse({
            "success": True,
            "sale_id": sale.id,
            "redirect_url": reverse("sale")
        })

    # ---------------------------------------------------
    # 7) Resposta normal (form)
    # ---------------------------------------------------
    messages.success(request, f"Venda #{sale.id} criada com sucesso!")
    return redirect("sale")


# =====================================================
# 4️⃣ ATUALIZAÇÃO DE VENDA
# =====================================================
@login_required
@transaction.atomic
def sale_update(request, sale_id):
    """
    Edita uma venda existente (se for agendada ou não concluída).
    """
    sale = get_object_or_404(Sale, id=sale_id)

    if request.method == "POST":
        sale.discount = Decimal(request.POST.get("discount") or 0)
        sale.status = request.POST.get("status", sale.status)
        sale.payment_method_id = request.POST.get("payment_method", sale.payment_method.id)
        sale.customer_id = request.POST.get("customer", sale.customer.id)
        sale.date = request.POST.get("scheduled_date", sale.date)

        sale.calculate_totals()
        sale.save()

        messages.success(request, f"Venda #{sale.id} atualizada com sucesso!")
        return redirect("sale")

    return render(request, "sale/sale_edit.html", {"sale": sale})


# =====================================================
# 5️⃣ EXCLUSÃO DE VENDA
# =====================================================
@login_required
@transaction.atomic
def sale_delete(request, sale_id):
    """
    Deleta uma venda (restaura estoque, se for concluída).
    Retoarna JSON idependentemente do tipo de requisição.
    """
    sale = get_object_or_404(Sale, id=sale_id)

    if request.method == "POST":
        if sale.status == "completed":
            # restaura o estoque
            for item in sale.items.all():
                item.product.stock += item.quantity
                item.product.save()

        sale.delete()
        json_response = {
            "success": True,
            "message": f"Venda #{sale_id} deletada com sucesso."
        }
        return JsonResponse(json_response)

    json_response = {
        "success": False,
        "error": "Método inválido."
    }
    return JsonResponse(json_response, status=400)
