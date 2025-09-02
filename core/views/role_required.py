from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from typing import Callable, TypeVar, Any
from django.http import (
    HttpRequest,
    HttpResponse,
)


F = TypeVar("F", bound=Callable[..., HttpResponse])


def role_required(role: str) -> Callable[[F], F]:
    def decorator(view_func: F) -> F:
        @login_required
        def _wrapped_view(
            request: HttpRequest,
            *args: Any,
            **kwargs: Any,
        ) -> HttpResponse:

            if getattr(request.user, "role", None) == role:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("Acesso não permitido.")

        return _wrapped_view  # type: ignore
    return decorator


# @role_required("admin")
# def dashboard_admin(request):
#     return render(request, "admin_dashboard.html")
