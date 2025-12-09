from django.urls import path
from ..views.user_view import UserView

user_view = UserView()

urlpatterns = [
    path(
        '',
        user_view.list_users,
        name='user_list'
    ),
    path(
        '<int:user_id>/',
        user_view.get_user,
        name='user_detail'
    ),
    path(
        'create/',
        user_view.create_user,
        name='user_create'
    ),
    path(
        '<int:user_id>/update/',
        user_view.update_user,
        name='user_update'
    ),
    path(
        '<int:user_id>/delete/',
        user_view.delete_user,
        name='user_delete'
    ),
    path(
        'change-password/',
        user_view.change_owen_password,
        name='user_change_password'
    ),
]
