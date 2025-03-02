from django.http import HttpResponse, JsonResponse


def ping(request):
    return JsonResponse({'ping': 'pong'}, status=200)

def index(request):
    return HttpResponse('Hello, world!')