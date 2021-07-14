from django.utils.deprecation import MiddlewareMixin
from utils.dbs import R

Rdb = R.getDB()


class ResetCookiesMiddleware(MiddlewareMixin):
    @staticmethod
    def process_response(request, response):
        global Rdb
        if request.COOKIES.get('token') is not None and request.COOKIES.get('token') != '' and Rdb.hget(
                request.COOKIES.get('token'), 'id') is not None:
            Rdb.expire(request.COOKIES.get('token'), 1800)
            response.set_cookie('token', request.COOKIES.get('token'), max_age=1800)
        return response
