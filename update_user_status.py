from db_connect import get_connection

def update_user_status(user_id):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT cumulative_done, cumulative_cancel, koruniv_verified, review_rate
                FROM User
                WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()

            if not user:
                return

            done = user['cumulative_done'] or 0
            cancel = user['cumulative_cancel'] or 0
            verified = user['koruniv_verified']
            rate = user['review_rate'] or 0.0

            # penalty는 문자열로 처리해야 함
            penalty = None
            if cancel >= 3:
                penalty = '5' if verified == 0 else '3'
            elif cancel >= 2 and verified == 0:
                penalty = '3'

            # 뱃지도 ENUM이므로 문자열
            badge = None
            if cancel >= 3:
                badge = None
            elif done >= 2 and rate >= 4.0:
                badge = "OB" if cancel == 2 else "GB"

            cursor.execute("""
                UPDATE User
                SET badge = %s,
                    penalty = %s
                WHERE user_id = %s
            """, (badge, penalty, user_id))
            print("🚩 유저 상태 업데이트 완료! badge:", badge, "/ penalty:", penalty)

            conn.commit()
    except Exception as e:
        print("🚨 유저 상태 업데이트 실패:", e)
    finally:
        if conn:
            conn.close()
