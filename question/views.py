import hashlib
import json
import random
import time
from copy import copy
from io import BytesIO
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import pandas as pd
from bson import ObjectId
from django.views.decorators.cache import cache_page

from utils.dbs import R, M
from utils.email import sendEmail

Mdb = M.getDB()
Rdb = R.getDB()
Domain = 'http://1506607292.top'


class VerifyToken:
    def dispatch(self, request, *args, **kwargs):
        if request.COOKIES.get('token') and Rdb.hexists(request.COOKIES.get('token'), 'id'):
            return super().dispatch(request, *args, **kwargs)
        return JsonResponse({
            'code': 1,
            'message': '验证错误请重新登录'
        })


class DecodeRequestBody(object):
    def __init__(self):
        self.data = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.data = json.loads(request.body)
        except Exception as e:
            print(e)
        return super().dispatch(request, *args, **kwargs)


class Respondent(DecodeRequestBody, VerifyToken, View):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            item = []
            for i in Mdb.respondent.find({'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id'))}):
                del i['_id']
                i['id'] = i['sid']
                del i['sid']
                item.append(i)
            return JsonResponse({
                'code': 0,
                'data': item,
                'message': '成功获取受访者列表'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    @staticmethod
    def post(request, *args, **kwargs):
        if not request.FILES:
            return JsonResponse({
                'code': 2,
                'message': '没有上传文件'
            })
        try:
            file = None
            for i in request.FILES:
                file = i
                break
            file = request.FILES[file]
            if file:
                fp = BytesIO()
                for chunk in file.chunks():
                    fp.write(chunk)
                data = pd.read_excel(fp).values
                for ii in data:
                    Mdb.respondent.delete_one(
                        {'sid': ii[0], 'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id'))})
                    Mdb.respondent.insert_one(
                        {'sid': ii[0], 'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id')),
                         'name': ii[1], 'school': ii[2],
                         'major': ii[3], 'Class': ii[4], 'sex': ii[5],
                         'phone': ii[6], 'email': ii[7],
                         })
                fp.close()
                return JsonResponse({
                    'code': 0,
                    'message': '上传成功'
                })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def delete(self, request, *args, **kwargs):
        try:
            for i in self.data:
                Mdb.respondent.delete_one({'sid': i, 'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id'))})
            return JsonResponse({
                'code': 0,
                'message': '删除成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e),
            })

    def put(self, request, *args, **kwargs):
        Mdb.respondent.update({'sid': self.data['id'], 'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id'))},
                              {'name': self.data['name']})
        return JsonResponse({
            'code': 2,
            'message': 'change respondent'
        })


class QuestionManage(VerifyToken, DecodeRequestBody, View):
    @staticmethod
    def getPage(pid):
        page = Mdb.page.find_one({'_id': ObjectId(pid)})
        page['id'] = str(page['_id'])
        del page['_id']
        questions = Mdb.question.find({'_id': {'$in': [ObjectId(i) for i in page['questionSet']]}})
        page['questionSet'] = []
        for i in questions:
            i['id'] = str(i['_id'])
            del i['_id']
            page['questionSet'].append(i)
        return page

    @staticmethod
    def get(request, *args, **kwargs):
        if request.GET.get('id') is None:
            try:
                item = []
                for i in Mdb.page.find(
                        {'user_ids': {'$elemMatch': {'$eq': int(Rdb.hget(request.COOKIES.get('token'), 'id'))}}}):
                    i['id'] = str(i['_id'])
                    del i['_id']
                    item.append(i)
                return JsonResponse({
                    'code': 0,
                    'data': item,
                    'message': '成功获取问卷'
                })
            except Exception as e:
                print(e)
                return JsonResponse({
                    'code': -1,
                    'message': str(e)
                })

        else:
            try:
                page = QuestionManage.getPage(request.GET.get('id'))
                return JsonResponse({
                    'code': 0,
                    'data': page,
                    'message': '成功获取问卷'
                })
            except Exception as e:
                print(e)
                return JsonResponse({
                    'code': -1,
                    'message': str(e),
                })

    def post(self, request, *args, **kwargs):
        try:
            self.data['user_ids'] = [int(Rdb.hget(request.COOKIES.get('token'), 'id'))]
            self.data['user_id'] = int(Rdb.hget(request.COOKIES.get('token'), 'id'))
            self.data['respondent'] = []
            pid = Mdb.page.insert_one(self.data).inserted_id
            return JsonResponse({
                'code': 0,
                'message': '创建问卷成功',
                'data': {'id': str(pid)}
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e),
            })

    def delete(self, request, *args, **kwargs):
        try:
            page = Mdb.page.find_one({'_id': ObjectId(self.data['id'])})
            Mdb.question.delete_many({'_id': {'$in': [ObjectId(i) for i in page['questionSet']]}})
            Mdb.u_p.delete_many({'pid': self.data['id']})
            Mdb.page.delete_one({'_id': ObjectId(self.data['id'])})
            return JsonResponse({
                'code': 0,
                'message': '删除成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def put(self, request, *args, **kwargs):
        try:
            _id = copy(self.data['id'])
            del self.data['id']
            del self.data['respondent']
            page = Mdb.page.find_one({'_id': ObjectId(_id)})
            deleteList = copy(page['questionSet'])
            for i in self.data['questionSet']:
                if 'id' in i:
                    deleteList.remove(i['id'])
                    if i['id'] in page['questionSet']:
                        item = copy(i['id'])
                        del i['id']
                        del i['respondent']
                        del i['answer']
                        Mdb.question.update({'_id': ObjectId(item)}, {'$set': i})
                else:
                    i['answer'] = {}
                    if i['type'] == 1:
                        for j in i['options']:
                            i['answer'][j['label']] = []
                    i['respondent'] = []
                    insertedId = Mdb.question.insert_one(i).inserted_id
                    Mdb.page.update({'_id': ObjectId(_id)}, {'$push': {'questionSet': str(insertedId)}})
            del self.data['questionSet']
            Mdb.page.update({'_id': ObjectId(_id)}, {'$pullAll': {'questionSet': deleteList}})
            Mdb.question.delete_many(
                {'_id': {'$in': [ObjectId(i) for i in deleteList]}})

            Mdb.page.update({'_id': ObjectId(_id)}, {'$set': self.data})
            return JsonResponse({
                'code': 0,
                'message': '更新成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })


class Share(DecodeRequestBody, VerifyToken, View):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            share = Mdb.share.find_one({'_id': ObjectId(request.GET.get('sessionid'))})
            if not share:
                return JsonResponse({
                    'code': 2,
                    'message': '链接不存在',
                })
            return JsonResponse({
                'code': 0,
                'message': '分享成功',
                'data': share
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def post(self, request, *args, **kwargs):
        try:
            password = str(random.randint(0, 1000000)).zfill(6)
            insertedId = Mdb.share.insert_one({'pid': self.data['id'], 'password': password,
                                               'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id'))}).insertedId
            return JsonResponse({
                'code': 0,
                'message': '分享成功',
                'data': {'password': password, 'sessionid': insertedId}
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def put(self, request, *args, **kwargs):
        try:
            share = Mdb.share.find_one(
                {'_id': ObjectId(request.GET.get('sessionid')), 'password': self.data['password']})
            if not share:
                return JsonResponse({
                    'code': 2,
                    'message': '密码或网址错误',
                })
            Mdb.page.update({'_id': ObjectId(share['pid'])},
                            {'$addToSet': {'user_ids': int(Rdb.hget(request.COOKIES.get('token'), 'id'))}})
            return JsonResponse({
                'code': 0,
                'message': '成功获取问卷',
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def delete(self, request, *args, **kwargs):
        password = str(random.randint(0, 1000000)).zfill(6)
        Mdb.share.insert_one({'pid': self.data['id']})


class Generate(VerifyToken, DecodeRequestBody, View):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            userList = []
            item = []
            for i in Mdb.u_p.find({'pid': str(request.GET.get('id'))}):
                item.append(i['rid'])
            for i in Mdb.respondent.find({'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id'))}):
                if str(i['_id']) not in item:
                    userList.append(
                        {'id': str(i['_id']), 'sid': i['sid'], 'name': i['name'], 'school': i['school'],
                         'sex': i['sex'], 'phone': i['phone'], 'email': i['email'], 'status': False})
                else:
                    userList.append(
                        {'id': str(i['_id']), 'sid': i['sid'], 'name': i['name'], 'school': i['school'],
                         'sex': i['sex'], 'phone': i['phone'], 'email': i['email'], 'status': True})
            return JsonResponse({
                'code': 0,
                'data': userList,
                'message': '成功获取信息'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def post(self, request, *args, **kwargs):
        try:
            page = Mdb.page.find_one({'_id': ObjectId(self.data['id'])})
            emailList = []
            for i in Mdb.respondent.find({'user_id': int(Rdb.hget(request.COOKIES.get('token'), 'id')),
                                          '_id': {'$in': [ObjectId(j) for j in self.data['userList']]}}):
                ranStr = random.randint(0, 1000000)
                sessionId = hashlib.md5(
                    (str(ranStr) + str(i['_id']) + str(self.data['id'])).encode('utf-8')).hexdigest()
                Mdb.u_p.insert_one({'pid': str(page['_id']), 'rid': str(i['_id']), 'sessionId': sessionId})
                emailList.append((i['email'], 'The open question URL for you',
                                  page['desc'] + '      ' + Domain + '/survey/' + sessionId))
            sendEmail(emailList)
            if page['open'] is False:
                return JsonResponse({
                    'code': 0,
                    'message': '发送问卷成功',
                })
            elif page['open'] is True:
                item = Mdb.u_p.find_one({'pid': self.data['id']})
                if not item:
                    sessionId = hashlib.md5(str(self.data['id']).encode('utf-8')).hexdigest()
                    Mdb.u_p.insert_one(
                        {'pid': str(page['_id']), 'rid': 'public_id_183400000000', 'sessionId': sessionId})
                    item = Mdb.u_p.find_one({'pid': self.data['id']})
                return JsonResponse({
                    'code': 0,
                    'message': '发送问卷成功',
                    'data': {'link': Domain + '/survey/' + item['sessionId']}
                })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })


class QuestionAnswer(DecodeRequestBody, View):
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs):
        try:
            item = Mdb.u_p.find_one({'sessionId': request.GET.get('sessionid')})
            if not item:
                return JsonResponse({
                    'code': 2,
                    'data': {'statusCode': 105},
                    'message': '无效sessionId'
                })
            if 'answer' in item:
                return JsonResponse({
                    'code': 2,
                    'data': {'statusCode': 104},
                    'message': '你已经答过这页问卷了'
                })
            page = QuestionManage.getPage(item['pid'])
            if item['rid'] == 'public_id_183400000000':
                if page['open'] is False:
                    return JsonResponse({
                        'code': 2,
                        'data': {'statusCode': 100},
                        'message': '链接暂未开放'
                    })
            if page['running'] is False:
                return JsonResponse({
                    'code': 2,
                    'data': {'statusCode': 100},
                    'message': '暂未允许答题'
                })
            if page['startTime'] is not None or page['stopTime'] is not None:
                if time.localtime(time.time()) > time.strptime(page['stopTime'], "%Y-%m-%d %H:%M:%S"):
                    return JsonResponse({
                        'code': 2,
                        'data': {'statusCode': 101},
                        'message': '问卷已停止收集'
                    })
                if time.localtime(time.time()) < time.strptime(page['startTime'], "%Y-%m-%d %H:%M:%S"):
                    return JsonResponse({
                        'code': 2,
                        'data': {'statusCode': 102},
                        'message': '问卷还未开始'
                    })
            page['statusCode'] = 103
            return JsonResponse({
                'code': 0,
                'data': page,
                'message': '成功获取信息'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })

    def post(self, request, *args, **kwargs):
        item = Mdb.u_p.find_one({'sessionId': request.GET.get('sessionid')})
        if not item:
            return JsonResponse({
                'code': 2,
                'message': '无效的sessionId'
            })
        if item['rid'] == 'public_id_183400000000':
            page = Mdb.page.find_one({'_id': ObjectId(item['pid'])})
            if page['open'] is False:
                return JsonResponse({
                    'code': 2,
                    'data': {'statusCode': 100},
                    'message': '链接暂未开放'
                })
        try:
            for i in self.data['questionSet']:
                if i['answer'] is None or i['answer'] == '':
                    continue
                elif type(i['answer']) is list:
                    for j in i['answer']:
                        Mdb.question.update({'_id': ObjectId(i['id'])},
                                            {'$push': {'answer.' + j: item['rid']}})
                    Mdb.question.update({'_id': ObjectId(i['id'])},
                                        {'$push': {'respondent': item['rid']}})
                else:
                    i['answer'] = i['answer'].replace('.', '。')
                    Mdb.question.update({'_id': ObjectId(i['id'])},
                                        {'$push': {'answer.' + i['answer']: item['rid'],
                                                   'respondent': item['rid']}})
            Mdb.page.update({'_id': ObjectId(item['pid'])}, {'$push': {'respondent': item['rid']}})
            if not item['rid'] == 'public_id_183400000000':
                Mdb.u_p.update({'sessionId': request.GET.get('sessionid')},
                               {'$set': {'answer': self.data}})
            return JsonResponse({
                'code': 0,
                'message': '提交问卷成功'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })


class QuestionResult(VerifyToken, View):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            page = QuestionManage.getPage(request.GET.get('id'))
            page['frequency'] = len(page['respondent'])
            questionSet = page['questionSet']
            for i in questionSet:
                i['frequency'] = len(i['respondent'])
                for j in i['answer']:
                    i['answer'][j] = len(i['answer'][j])
            for i in questionSet:
                if i['type'] == 0:
                    answer = i['answer']
                    answerList = []
                    for j in answer:
                        answerList.append({j: answer[j]})
                    i['answer'] = answerList
            return JsonResponse({
                'code': 0,
                'message': '拿到结果了',
                'data': page
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': -1,
                'message': str(e)
            })
