import tkinter as tk
from tkinter import messagebox
from appointment_list_gui import open_appointment_list
from appointment_borrowed_list_gui import open_borrowed_appointment_list
from transaction_list_gui import (
    open_transaction_list,
    open_cancelled_transaction_list,
    open_confirmed_transaction_list,
    open_other_cancelled_transaction_list,
    open_expired_transaction_list
)
from db_connect import get_connection
from update_user_status import update_user_status


def open_appointment_manager(user_id):
    win = tk.Toplevel()
    win.title("📅 약속 관리")
    win.geometry("300x200")

    btn_receive = tk.Button(
        win,
        text="수신 약속 목록",
        width=25,
        command=lambda: open_appointment_list(user_id)
    )
    btn_receive.pack(pady=10)

    btn_proposed = tk.Button(
        win,
        text="제안한 약속 목록",
        width=25,
        command=lambda: open_borrowed_appointment_list(user_id)
    )
    btn_proposed.pack(pady=10)

    btn_close = tk.Button(
        win,
        text="닫기",
        width=10,
        command=win.destroy
    )
    btn_close.pack(pady=10)


def open_transaction_manager(user_id):
    win = tk.Toplevel()
    win.title("🛒 거래 관리")
    win.geometry("400x300")

    btn_pending = tk.Button(
        win,
        text="⏳ 진행 중 거래",
        width=30,
        command=lambda: open_transaction_list(user_id)
    )
    btn_pending.pack(pady=5)

    btn_confirmed = tk.Button(
        win,
        text="✅ 완료된 거래",
        width=30,
        command=lambda: open_confirmed_transaction_list(user_id)
    )
    btn_confirmed.pack(pady=5)

    btn_my_cancelled = tk.Button(
        win,
        text="❌ 내가 취소한 거래",
        width=30,
        command=lambda: open_cancelled_transaction_list(user_id)
    )
    btn_my_cancelled.pack(pady=5)

    btn_other_cancelled = tk.Button(
        win,
        text="🚫 상대방이 취소한 거래",
        width=30,
        command=lambda: open_other_cancelled_transaction_list(user_id)
    )
    btn_other_cancelled.pack(pady=5)

    btn_expired = tk.Button(
        win,
        text="⏰ 만료된 거래",
        width=30,
        command=lambda: open_expired_transaction_list(user_id)
    )
    btn_expired.pack(pady=5)

    btn_close = tk.Button(
        win,
        text="닫기",
        width=10,
        command=win.destroy
    )
    btn_close.pack(pady=10)


def open_mypage(user_id):
    win = tk.Toplevel()
    win.title("마이페이지")
    win.geometry("300x350")

    # 사용자 정보 조회
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT nickname, email, review_rate, review_count, badge, penalty, cumulative_done, cumulative_cancel FROM User WHERE user_id=%s",
                (user_id,)
            )
            user = cur.fetchone() or {}
            nickname = user.get('nickname', 'Unknown')
            email = user.get('email', '')
            review_rate = user.get('review_rate') or 0
            review_count = user.get('review_count') or 0
            badge = user.get('badge') or '신규'
            penalty = user.get('penalty') or 0
            done_count = user.get('cumulative_done') or 0
            cancel_count = user.get('cumulative_cancel') or 0
    except Exception as e:
        messagebox.showerror("DB 오류", str(e))
        nickname, email = 'Unknown', ''
        review_rate, review_count = 0, 0
        badge, penalty = '신규', 0
        done_count, cancel_count = 0, 0
    finally:
        conn.close()

    # 헤더: 닉네임, 이메일, 유저ID (가운데 정렬, 글씨 크게)
    header = tk.Label(
        win,
        text=f"닉네임: {nickname}\n이메일: {email}\n아이디: {user_id}",
        font=("Arial", 16, "bold"),
        pady=10,
        justify="center"
    )
    header.pack()

    # 리뷰 및 상태 정보
    info_frame = tk.Frame(win)
    info_frame.pack(pady=5)

    lbl_review = tk.Label(
        info_frame,
        text=f"⭐ 리뷰: {review_rate:.2f}/5 ({review_count}회)",
        font=("Arial", 12)
    )
    lbl_review.pack()

    lbl_badge = tk.Label(
        info_frame,
        text=f"🏅 뱃지: {badge}",
        font=("Arial", 12)
    )
    lbl_badge.pack()

    lbl_penalty = tk.Label(
        info_frame,
        text=f"⛔ 정지: {penalty}일", 
        font=("Arial", 12)
    )
    lbl_penalty.pack()

    lbl_done = tk.Label(
        info_frame,
        text=f"✅ 완료: {done_count}회", 
        font=("Arial", 12)
    )
    lbl_done.pack()

    lbl_cancel = tk.Label(
        info_frame,
        text=f"❌ 취소: {cancel_count}회", 
        font=("Arial", 12)
    )
    lbl_cancel.pack()

    # 기능 버튼 (세로 스택)
    btn_appt = tk.Button(
        win,
        text="📅 약속 관리",
        width=25,
        command=lambda: open_appointment_manager(user_id)
    )
    btn_appt.pack(pady=8)

    btn_tx = tk.Button(
        win,
        text="🛒 거래 관리",
        width=25,
        command=lambda: open_transaction_manager(user_id)
    )
    btn_tx.pack(pady=8)

    btn_close = tk.Button(
        win,
        text="닫기",
        width=10,
        command=win.destroy
    )
    btn_close.pack(pady=20)


# 예시 실행
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_mypage(user_id=70)
    root.mainloop()
