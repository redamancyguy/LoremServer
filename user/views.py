import json
import base64
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import jwt
import random

from django.views.decorators.cache import cache_page

from . import models
from utils.dbs import R
from utils.generateImage import codeImage
from utils.email import sendEmail

Rdb = R.getDB()


class DecodeRequestBody:
    def __init__(self):
        self.data = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.data = json.loads(request.body)
        except Exception as e:
            print(e)
        return super().dispatch(request, *args, **kwargs)


class VerifyCode:
    def dispatch(self, request, *args, **kwargs):
        if Rdb.get('captcha' + self.data['captcha']['id']) != self.data['captcha']['code']:
            return JsonResponse({
                'code': 2,
                'message': '验证码错误'
            })
        else:
            return super().dispatch(request, *args, **kwargs)


class Login(DecodeRequestBody, VerifyCode, View):
    def post(self, request, *args, **kwargs):
        try:
            user = models.User.objects.filter(username=self.data['username'],
                                              password=self.data['password']).first()
            user1 = models.User.objects.filter(email=self.data['username'],
                                               password=self.data['password']).first()
            if not user1 and not user:
                return JsonResponse({
                    'code': 2,
                    'message': '用户名或密码错误'
                })
            if not user:
                user = user1
            key = str(random.randint(0, 1000000))
            payload = {'username': user.username}
            token = jwt.encode(payload, key, algorithm='HS256')
            Rdb.hset(token, 'id', str(user.id))
            Rdb.hset(token, 'dynamicCode', key)
            Rdb.expire(token, 1800)
            response = JsonResponse({
                'code': 0,
                'message': '登录成功'
            })
            response.set_cookie('token', token, max_age=1800)
            response.set_cookie('username', self.data['username'])
            return response
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })


class Logout(View):
    @staticmethod
    def post(request, *args, **kwargs):
        try:
            if request.COOKIES.get('token'):
                Rdb.delete(request.COOKIES.get('token'))
                response = JsonResponse({
                    'code': 0,
                    'message': '注销成功'
                })
                response.delete_cookie('token')
                return response
            return JsonResponse({
                'code': 2,
                'massage': '您已注销'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'massage': str(e)
            })


class ChangePassword(DecodeRequestBody, View):
    def post(self, request, *args, **kwargs):
        try:
            if Rdb.get('captcha' + self.data['captcha']['id']) != self.data['captcha']['code']:
                return JsonResponse({
                    'code': 2,
                    'message': '验证码错误'
                })
            user = models.User.objects.get(email=self.data['email'])
            if not user:
                return JsonResponse({
                    'code': 2,
                    'message': '此邮箱还未注册，请先注册后再登陆'
                })
            emailCode = str(random.randint(0, 1000000)).zfill(6)
            user.emailCode = emailCode
            user.save()
            sendEmail([(user.email, '更改密码的密钥',
                        '这是您用来更改您的密码所需要的密钥，请及时利用密钥更改您的密码' + emailCode)])
            return JsonResponse({
                'code': 0,
                'message': '密钥已经发送至您的邮箱，请及时查看'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def put(self, request, *args, **kwargs):
        try:
            user = models.User.objects.get(emailCode=self.data['emailCode'])
            if not user:
                return JsonResponse({
                    'code': 2,
                    'message': '密钥错误'
                })
            if 'password' not in self.data:
                return JsonResponse({
                    'code': 0,
                    'message': '验证通过'
                })
            user.password = self.data['password']
            user.emailCode = str(random.randint(0, 1000000)).zfill(6)
            user.save()
            return JsonResponse({
                'code': 0,
                'message': '更改成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })


class Register(DecodeRequestBody, VerifyCode, View):
    def post(self, request, *args, **kwargs):
        try:
            models.User.objects.create(username=self.data['username'],
                                       password=self.data['password'],
                                       phone=self.data['phone'],
                                       email=self.data['email'], emailCode=str(random.randint(0, 1000000)).zfill(6))
            return JsonResponse({
                'code': 0,
                'massage': '注册成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'massage': str(e)
            })


class UserInfo(DecodeRequestBody, View):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            user = models.User.objects.get(id=int(Rdb.hget(request.COOKIES.get('token'), 'id')))
            data = model_to_dict(user)
            del data['password']
            del data['emailCode']
            return JsonResponse({'code': 0, 'data': data})
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'massage': str(e)
            })

    def put(self, request, *args, **kwargs):
        try:
            if 'id' in self.data:
                self.data.pop('id')
            if 'email' in self.data:
                self.data.pop('email')
            user = models.User.objects.get(id=int(Rdb.hget(request.COOKIES.get('token'), 'id')))
            if 'password' in self.data:
                if 'oldPassword' in self.data:
                    if self.data['oldPassword'] == user.password:
                        del self.data['oldPassword']
                        print('password', self.data)
                        models.User.objects.get(id=int(Rdb.hget(request.COOKIES.get('token'), 'id'))).update(
                            **self.data)
                    else:
                        return JsonResponse({
                            'code': 2,
                            'message': '密码错误'
                        })
            else:
                models.User.objects.get(id=int(Rdb.hget(request.COOKIES.get('token'), 'id'))).update(**self.data)
            return JsonResponse({
                'code': 0,
                'massage': '更改成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'massage': str(e)
            })


def getCaptcha(request):
    source = '0123456789'
    data = ''
    for i in range(4):
        data += random.choice(source)
    base64Data = base64.b64encode(codeImage(data))
    if int(Rdb.get('captchaCount')) > 2 ** 16 - 1:
        Rdb.set('captchaCount', 0)
    item = Rdb.incr('captchaCount', 1)
    Rdb.setex('captcha' + str(item), 45, data)
    return JsonResponse({
        'code': 0,
        'message': '成功获取验证码',
        'data': {'id': str(item),
                 'base64Data': str(base64Data, encoding='utf-8')}
    })
