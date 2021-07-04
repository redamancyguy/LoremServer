from django.shortcuts import redirect
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
        print('test',request.META)
        response['test'] = 'test'
        # return redirect('/api/'+request.path)
        return response
