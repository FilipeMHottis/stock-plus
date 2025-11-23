from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models.payment_method import PaymentMethod
from django.http import HttpRequest, JsonResponse
from ..utils.role_required import role_required
from ..models.sale import Sale
from django.utils.timezone import now, timedelta


@login_required
def report(request: HttpRequest):
    """Lista todos os métodos de pagamento."""
    methods = PaymentMethod.objects.all()
    sales = Sale.objects.all()        

    return render(
        request, 
        "report/report.html",
        {
            "payment_methods": methods,
            "sales_history": sales
        }
    )


@login_required
def sales_list_api(request):
    page = int(request.GET.get("page", 1))
    per_page = 10

    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    date_filter = request.GET.get("date", "")

    sales = Sale.objects.select_related("customer").order_by("-date")

    # 🔍 Texto
    if search:
        sales = sales.filter(
            customer__name__icontains=search
        ) | sales.filter(id__icontains=search)

    # 🎯 Status
    if status:
        sales = sales.filter(status=status)

    # 📅 Filtro de data
    if date_filter == "today":
        sales = sales.filter(date__date=now().date())
    elif date_filter == "yesterday":
        sales = sales.filter(date__date=now().date() - timedelta(days=1))
    elif date_filter.isdigit():
        days = int(date_filter)
        sales = sales.filter(date__gte=now() - timedelta(days=days))

    total = sales.count()

    # PAGINAÇÃO
    start = (page - 1) * per_page
    end = start + per_page

    sales_page = sales[start:end]

    results = [
        {
            "id": s.id,
            "date": s.date.strftime("%d/%m/%Y %H:%M"),
            "customer": s.customer.name,
            "total": float(s.total_amount),
            "status": s.status,
        }
        for s in sales_page
    ]

    return JsonResponse({
        "success": True,
        "sales": results,
        "page": page,
        "has_next": end < total,
        "has_prev": page > 1,
    })


@login_required
def sale_detail_api(request, sale_id):
    """
    Retorna os detalhes completos de uma venda em formato JSON.
    """
    sale = get_object_or_404(Sale, id=sale_id)

    items = [
        {
            "product": item.product.name,
            "qty": item.quantity,
            "unit_price": float(item.unit_price),
            "subtotal": float(item.subtotal),
        }
        for item in sale.items.all()
    ]

    data = {
        "id": sale.id,
        "customer": {
            "id": sale.customer.id,
            "name": sale.customer.name,
            "trade_name": sale.customer.trade_name,
            "cnpjcpf": sale.customer.cnpj_or_cpf,
            "phone": sale.customer.phone,
            "address": sale.customer.address,
        },
        "discount": float(sale.discount),
        "total": float(sale.total_amount),
        "status": sale.status,
        "date": sale.date.strftime("%d/%m/%Y %H:%M"),
        "payment_method": sale.payment_method.name if sale.payment_method else "",
        "items": items,
    }

    return JsonResponse({"success": True, "sale": data})


@login_required
@role_required(["admin", "manager"])
def payment_create(request: HttpRequest):
    """Cria um novo método de pagamento."""
    if request.method == "POST":
        name = request.POST.get("name")
        type = request.POST.get("type")
        internal_fee = (
            request.POST.get("internal_fee")
            or 0
        )
        min_installment_amount = (
            request.POST.get("min_installment_amount")
            or 0
        )
        max_installments = (
            request.POST.get("max_installments")
            or 1
        )
        no_interest_installments = (
            request.POST.get("no_interest_installments")
            or 1
        )
        customer_interest_rate = (
            request.POST.get("customer_interest_rate")
            or 0
        )
        is_active = bool(request.POST.get("is_active"))

        try:
            method = PaymentMethod.objects.create(
                name=name,
                type=type,
                internal_fee=internal_fee,
                min_installment_amount=min_installment_amount,
                max_installments=max_installments,
                no_interest_installments=no_interest_installments,
                customer_interest_rate=customer_interest_rate,
                is_active=is_active,
            )
            method.full_clean()
            method.save()
            messages.success(
                request,
                "Método de pagamento criado com sucesso!"
            )
        except Exception as e:
            messages.error(request, f"Erro ao criar método: {e}")

    return redirect("report")  # ou outra página onde o card aparece


@login_required
@role_required(["admin", "manager"])
def payment_update(request: HttpRequest, method_id: int):
    """Atualiza um método existente."""
    method = get_object_or_404(PaymentMethod, id=method_id)

    if request.method == "POST":
        method.name = request.POST.get("name")
        method.type = request.POST.get("type")
        method.internal_fee = (
            request.POST.get("internal_fee")
            or 0
        )
        method.min_installment_amount = (
            request.POST.get("min_installment_amount")
            or 0
        )
        method.max_installments = (
            request.POST.get("max_installments")
            or 1
        )
        method.no_interest_installments = (
            request.POST.get("no_interest_installments")
            or 1
        )
        method.customer_interest_rate = (
            request.POST.get("customer_interest_rate")
            or 0
        )
        method.is_active = bool(request.POST.get("is_active"))

        try:
            method.full_clean()
            method.save()
            messages.success(
                request,
                "Método de pagamento atualizado com sucesso!"
            )
        except Exception as e:
            messages.error(request, f"Erro ao atualizar método: {e}")

    return redirect("report")


@login_required
@role_required(["admin", "manager"])
def payment_delete(request: HttpRequest, method_id: int):
    """Deleta um método de pagamento."""
    method = get_object_or_404(PaymentMethod, id=method_id)
    method.delete()
    messages.success(request, "Método de pagamento removido com sucesso!")
    return redirect("report")
