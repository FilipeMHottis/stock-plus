from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models.tag import Tag
from ..utils.role_required import role_required
from django.http import HttpRequest


@login_required
def tag(request: HttpRequest):
    tags = Tag.objects.all()
    return render(request, "tag.html", {"tags": tags})


@role_required(["admin", "checkout"])
@login_required
def tag_create(request: HttpRequest):
    if request.method == "POST":
        name = request.POST.get("name")
        color = request.POST.get("color")

        if not name:
            messages.error(request, "Nome é obrigatório.")
            return redirect("tag")

        Tag.objects.create(
            name=name,
            color=color,
        )
        messages.success(request, "Tag criada com sucesso.")
    return redirect("tag")


@role_required(["admin", "checkout"])
@login_required
def tag_update(request: HttpRequest, id: int):
    tag = get_object_or_404(Tag, id=id)

    if request.method == "POST":
        tag.name = (
            request.POST.get("name") or tag.name
        )
        tag.color = (
            request.POST.get("color") or tag.color
        )

        if not tag.name:
            messages.error(request, "Nome é obrigatório.")
            return redirect("tag")

        tag.save()
        messages.success(request, "Tag atualizada com sucesso.")
    return redirect("tag")


@role_required(["admin", "checkout"])
@login_required
def tag_delete(request: HttpRequest, id: int):
    tag = get_object_or_404(Tag, id=id)
    tag.delete()
    messages.success(request, "Tag deletada com sucesso.")
    return redirect("tag")
