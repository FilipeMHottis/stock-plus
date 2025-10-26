from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models.customer import Customer
from ..utils.role_required import role_required
from django.http import HttpRequest


@login_required
def customer(request: HttpRequest):
    customers = Customer.objects.all()
    return render(request, "customer/customer.html", {"customers": customers})


@role_required(["admin", "checkout"])
@login_required
def customer_create(request: HttpRequest):
    if request.method == "POST":
        name = request.POST.get("name")
        trade_name = request.POST.get("trade_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")

        if not name or not phone:
            messages.error(request, "Nome e telefone são obrigatórios.")
            return redirect("customer")

        Customer.objects.create(
            name=name,
            trade_name=trade_name,
            phone=phone,
            email=email,
            address=address,
        )
        messages.success(request, "Cliente criado com sucesso.")
    return redirect("customer")


@role_required(["admin", "checkout"])
@login_required
def customer_update(request: HttpRequest, id: int):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.name = (
            request.POST.get("name") or customer.name
        )
        customer.trade_name = (
            request.POST.get("trade_name") or customer.trade_name
        )
        customer.phone = (
            request.POST.get("phone") or customer.phone
        )
        customer.email = (
            request.POST.get("email") or customer.email
        )
        customer.address = (
            request.POST.get("address") or customer.address
        )

        if not customer.name or not customer.phone:
            messages.error(request, "Nome e telefone são obrigatórios.")
            return redirect("customer")

        customer.save()
        messages.success(request, "Cliente atualizado com sucesso.")
    return redirect("customer")


@role_required(["admin", "checkout"])
@login_required
def customer_delete(request: HttpRequest, id: int):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "Cliente excluído com sucesso.")
    return redirect("customer")
