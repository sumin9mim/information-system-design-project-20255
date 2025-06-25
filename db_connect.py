# db_connect.py

import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='sumin0213',   # ← 비밀번호 입력
        database='eend',   # ← DB 이름 입력
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
