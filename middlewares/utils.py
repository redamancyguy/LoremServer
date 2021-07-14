from django.http import QueryDict
from django.utils.deprecation import MiddlewareMixin


class HttpPost2HttpOtherMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        try:
            http_method = request.META['REQUEST_METHOD']
            if http_method.upper() not in ('GET', 'POST'):
                setattr(request, http_method.upper(), QueryDict(request.body))
        except Exception as e:
            print(e)
        finally:
            return None
