host = '39.104.209.232'
class Mongo:
    def __init__(self, host=host, port=27017):
        from pymongo import MongoClient
        self.__host = host
        self.__port = port
        self.__client = MongoClient(self.__host, self.__port)
        self.__database = self.__client.LoremServer  # use test as default

    def getClient(self):
        return self.__client

    def getDB(self, username='user', password='3325111'):
        self.__database.authenticate(username, password)
        return self.__database

    def changeHost(self, host):
        from pymongo import MongoClient
        self.__host = host
        self.__client = MongoClient(self.__host, self.__port)

    def __del__(self):
        self.__client.close()


class Redis:
    def __init__(self):
        import redis
        self.__db = redis.Redis(host=host, port=6379, decode_responses=True)

    def getDB(self):
        return self.__db

    def __del__(self):
        self.__db.close()


R = Redis()
M = Mongo()
