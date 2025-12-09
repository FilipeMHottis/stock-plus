from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ..models.user import User
from ..utils.role_required import role_required
from django.http import JsonResponse
from django.db import IntegrityError


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @role_required(['admin', 'manager', 'checkout'])
    def list_users(self, request):
        users = User.objects.all()
        users_data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
            for user in users
        ]
        return JsonResponse(
            {
                'status': 'success',
                'data': users_data
            },
            status=200
        )

    @role_required(['admin', 'manager', 'checkout'])
    def get_user(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
            return JsonResponse(
                {
                    'status': 'success',
                    'data': user_data
                },
                status=200
            )
        except User.DoesNotExist:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'User not found'
                },
                status=404
            )

    @role_required(['admin'])
    def delete_user(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'User deleted successfully'
                },
                status=200
            )
        except User.DoesNotExist:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'User not found'
                },
                status=404
            )

    @role_required(['admin', 'manager'])
    def create_user(self, request):
        data = request.POST
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'checkout')

        if not username or not email or not password:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Username, email, and password are required'
                },
                status=400
            )

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
        except IntegrityError:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Username or email already exists'
                },
                status=400
            )

        user.role = role
        user.save()

        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        }

        return JsonResponse(
            {
                'status': 'success',
                'data': user_data
            },
            status=201
        )

    @role_required(['admin', 'manager'])
    def update_user(self, request, user_id):
        data = request.POST
        try:
            user = User.objects.get(id=user_id)

            username = data.get('username')
            email = data.get('email')
            role = data.get('role')
            password = data.get('password')

            if username:
                user.username = username
            if email:
                user.email = email
            if role:
                user.role = role
            if password:
                user.set_password(password)

            user.save()

            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }

            return JsonResponse(
                {
                    'status': 'success',
                    'data': user_data
                },
                status=200
            )
        except User.DoesNotExist:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'User not found'
                },
                status=404
            )

    @role_required(['admin', 'manager', 'checkout'])
    def change_owen_password(self, request):
        data = request.POST
        user = request.user

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Old password and new password are required'
                },
                status=400
            )

        if not user.check_password(old_password):
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Old password is incorrect'
                },
                status=400
            )

        user.set_password(new_password)
        user.save()

        return JsonResponse(
            {
                'status': 'success',
                'message': 'Password changed successfully'
            },
            status=200
        )
