import hashlib
import pymysql
import sys
db = pymysql.connect(host='39.104.209.232', user='user', password='3325111', database='LoremServer')
cursor = db.cursor()

sql = "update user_user set password = '%s' where username = '%s' "%(hashlib.md5('www123456789'.encode()).hexdigest(),'sunwenli')
cursor.execute(sql)
result = cursor.fetchall()
for i in result:
    print(i)
cursor.close()
db.commit()
db.close()
sys.exit()