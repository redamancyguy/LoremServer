from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin
from utils.dbs import R

Rdb = R.getDB()


class Test(MiddlewareMixin):

    @staticmethod
    def process_request(request):
        pass

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # return callback(request, *callback_args, **callback_kwargs)
        pass

    @staticmethod
    def process_exception(request, exception):
        pass

    @staticmethod
    def process_response(request, response):
        print(get_token(request))
        if not get_token(request):
            response.set_cookie('csrftoken', get_token(request))
        return response
