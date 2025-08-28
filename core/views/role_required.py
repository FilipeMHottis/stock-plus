from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(role):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Acesso não permitido.")
        return _wrapped_view
    return decorator


# @role_required("admin")
# def dashboard_admin(request):
#     return render(request, "admin_dashboard.html")
