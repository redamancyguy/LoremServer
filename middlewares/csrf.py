import random
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from utils.dbs import R

Rdb = R.getDB()


class CsrfVerifyMiddleware(MiddlewareMixin):

    @staticmethod
    def process_request(request):
        if not request.META.get('HTTP_CSRFSTATICCODE') or not Rdb.hget(request.META.get('HTTP_CSRFSTATICCODE'),
                                                                       'tempCode') == request.META.get(
            'HTTP_CSRFDYNAMICCODE'):
            # response = redirect('/api/' + request.path)
            response = JsonResponse({'code': 5, 'message': '动态验证错误'})
            response.status_code = 403
            return response

    @staticmethod
    def process_response(request, response):
        csrfStaticCode = request.META.get('HTTP_CSRFSTATICCODE')
        if csrfStaticCode is None:
            csrfStaticCode = str(random.randint(0, 100000000000)).zfill(12)
        response['csrfStaticCode'] = csrfStaticCode
        csrfDynamicCode = str(random.randint(0, 100000000000)).zfill(12)
        response['csrfDynamicCode'] = csrfDynamicCode
        Rdb.hset(csrfStaticCode, 'tempCode', csrfDynamicCode)
        print(csrfDynamicCode)
        Rdb.expire(csrfStaticCode, 1800)
        return response

    @staticmethod
    def process_template_response(request, response):
        return response
