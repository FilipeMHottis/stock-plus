from .urls_path.user_url import urlpatterns as user_urlpatterns
from .views.online_api import online_api_view
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', online_api_view),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', include((user_urlpatterns, 'users'))),
]
