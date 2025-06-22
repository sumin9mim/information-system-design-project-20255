# post_utils.py

from db_connect import get_connection

def save_post(title, content, author_email):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO Post (title, content, author_email)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (title, content, author_email))
            conn.commit()
        conn.close()
        return True, "✅ 게시글 저장 완료!"
    except Exception as e:
        return False, f"❌ 게시글 저장 실패: {e}"
