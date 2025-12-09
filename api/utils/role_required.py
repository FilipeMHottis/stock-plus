from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            # Autenticar o usuário usando JWT
            jwt_token = JWTAuthentication()
            try:
                user_auth_tuple = jwt_token.authenticate(request)
                if user_auth_tuple is None:
                    return JsonResponse(
                        {
                            'status': 'error',
                            'message': 'Autenticação obrigatória.'
                        },
                        status=401
                    )
                request.user, _ = user_auth_tuple
            except Exception:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Token inválido.'
                    },
                    status=401
                )

            user = getattr(request, 'user', None)
            user_role = getattr(user, "role", None)

            # Check se o usuário está autenticado
            if not user or not user.is_authenticated:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Autenticação obrigatória.'
                    },
                    status=401
                )

            # Check se o papel do usuário está na lista de papéis permitidos
            if user_role not in roles:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Acesso não permitido.'
                    },
                    status=403
                )

            return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator
