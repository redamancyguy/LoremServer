import random
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from utils.dbs import R

Rdb = R.getDB()


class CsrfVerifyMiddleware(MiddlewareMixin):

    @staticmethod
    def process_request(request):
        print(request.META.get('HTTP_CSRFTOKEN'))
        if not request.META.get('HTTP_CSRFTOKEN') or not Rdb.hget(request.META.get('HTTP_CSRFTOKEN')[:15],
                                                                  'tempCode') == request.META.get(
            'HTTP_CSRFTOKEN')[15:]:
            response = JsonResponse({'code': 5, 'message': '动态验证错误'})
            # response.status_code = 403
            return response

    @staticmethod
    def process_response(request, response):
        csrfStaticCode = request.META.get('HTTP_CSRFTOKEN')[:15]
        if csrfStaticCode is None:
            csrfStaticCode = str(random.randint(0, 100000000000000)).zfill(15)
        csrfDynamicCode = str(random.randint(0, 100000000000000)).zfill(15)
        response['CsrfToken'] = csrfStaticCode + csrfDynamicCode
        Rdb.hset(csrfStaticCode, 'tempCode', csrfDynamicCode)
        Rdb.expire(csrfStaticCode, 1800)
        return response

    @staticmethod
    def process_template_response(request, response):
        return response
