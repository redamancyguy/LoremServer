from django.http import HttpResponse, JsonResponse
from django.views import View


class Index(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponse('Index')

    @staticmethod
    def post(request, *args, **kwargs):
        return HttpResponse('Index')


class NotFound(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponse('Not Found')

    @staticmethod
    def post(request, *args, **kwargs):
        return HttpResponse('Not Found')


def test(request):
    return JsonResponse({'code': 0, 'message': 'ok'})


def test1(request):
    return JsonResponse({'code': 0, 'message': 'ok1'})
