from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models.payment_method import PaymentMethod
from django.http import HttpRequest
from ..utils.role_required import role_required


@login_required
def report(request: HttpRequest):
    """Lista todos os métodos de pagamento."""
    methods = PaymentMethod.objects.all()
    return render(request, "report/report.html", {"payment_methods": methods})


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
