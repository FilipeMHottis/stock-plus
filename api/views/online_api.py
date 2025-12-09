from django.http import JsonResponse


def online_api_view(request):
    return JsonResponse(
        {
            'status': 'ok',
            'message': 'Online API is working'
        }
    )
