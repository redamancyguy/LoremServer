import pymysql

pymysql.install_as_MySQLdb()

from utils.dbs import R

Rdb = R.getDB()
Rdb.set('captchaCount', 0)