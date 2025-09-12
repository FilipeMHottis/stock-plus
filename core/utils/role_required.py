from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpRequest, HttpResponse
from typing import Callable, TypeVar, Any, Union

F = TypeVar("F", bound=Callable[..., HttpResponse])


def role_required(roles: Union[str, list[str]]) -> Callable[[F], F]:
    def decorator(view_func: F) -> F:
        @login_required
        def _wrapped_view(
            request: HttpRequest,
            *args: Any,
            **kwargs: Any,
        ) -> HttpResponse:

            user_role = getattr(request.user, "role", None)

            # Se roles for string, transforma em lista
            allowed_roles = [roles] if isinstance(roles, str) else roles

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("Acesso não permitido.")

        return _wrapped_view  # type: ignore
    return decorator
