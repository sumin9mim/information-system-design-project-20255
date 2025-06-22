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


# ------------- 약속 관리 창 ------------------------------------------------
def open_appointment_manager(user_id):
    win = tk.Toplevel()
    win.title("📅 약속 관리")
    win.geometry("300x200")

    tk.Button(
        win, text="수신 약속 목록", width=25,
        command=lambda: open_appointment_list(user_id)
    ).pack(pady=10)

    tk.Button(
        win, text="제안한 약속 목록", width=25,
        command=lambda: open_borrowed_appointment_list(user_id)
    ).pack(pady=10)

    tk.Button(win, text="닫기", width=10, command=win.destroy).pack(pady=10)


# ------------- 거래 관리 창 -------------------------------------------------
def open_transaction_manager(user_id):
    win = tk.Toplevel()
    win.title("🛒 거래 관리")
    win.geometry("400x300")

    tk.Button(
        win, text="⏳ 진행 중 거래", width=30,
        command=lambda: open_transaction_list(user_id)
    ).pack(pady=5)

    tk.Button(
        win, text="✅ 완료된 거래", width=30,
        command=lambda: open_confirmed_transaction_list(user_id)
    ).pack(pady=5)

    tk.Button(
        win, text="❌ 내가 취소한 거래", width=30,
        command=lambda: open_cancelled_transaction_list(user_id)
    ).pack(pady=5)

    tk.Button(
        win, text="🚫 상대방이 취소한 거래", width=30,
        command=lambda: open_other_cancelled_transaction_list(user_id)
    ).pack(pady=5)

    tk.Button(
        win, text="⏰ 만료된 거래", width=30,
        command=lambda: open_expired_transaction_list(user_id)
    ).pack(pady=5)

    tk.Button(win, text="닫기", width=10, command=win.destroy).pack(pady=10)


# ------------- 마이페이지 ---------------------------------------------------
def open_mypage(user_id):
    win = tk.Toplevel()
    win.title("마이페이지")
    win.geometry("300x350")

    # 0) 페이지 열릴 때 한 번 상태 갱신
    update_user_status(user_id)

    # 1) DB에서 사용자 정보 읽기 -----------------------------
    def fetch_user():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT nickname, email,
                           review_rate, review_count,
                           badge, penalty,
                           cumulative_done, cumulative_cancel
                    FROM User WHERE user_id=%s
                """, (user_id,))
                return cur.fetchone() or {}
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
            return {}
        finally:
            conn.close()

    user = fetch_user()
    nickname      = user.get('nickname', 'Unknown')
    email         = user.get('email', '')
    review_rate   = user.get('review_rate')   or 0
    review_count  = user.get('review_count')  or 0
    badge         = user.get('badge')         or '신규'
    penalty       = user.get('penalty')       or 0
    done_count    = user.get('cumulative_done')    or 0
    cancel_count  = user.get('cumulative_cancel')  or 0

    # 2) 헤더와 정보 라벨 ------------------------------------
    header = tk.Label(
        win,
        text=f"닉네임: {nickname}\n이메일: {email}\n아이디: {user_id}",
        font=("Arial", 16, "bold"),
        pady=10, justify="center"
    )
    header.pack()

    info_frame = tk.Frame(win); info_frame.pack(pady=5)

    lbl_review  = tk.Label(info_frame, font=("Arial", 12))
    lbl_badge   = tk.Label(info_frame, font=("Arial", 12))
    lbl_penalty = tk.Label(info_frame, font=("Arial", 12))
    lbl_done    = tk.Label(info_frame, font=("Arial", 12))
    lbl_cancel  = tk.Label(info_frame, font=("Arial", 12))

    for lbl in (lbl_review, lbl_badge, lbl_penalty, lbl_done, lbl_cancel):
        lbl.pack()

    # 3) 라벨 내용 업데이트 함수 ------------------------------
    def update_labels(u):
        header.config(
            text=f"닉네임: {u.get('nickname','Unknown')}\n"
                 f"이메일: {u.get('email','')}\n"
                 f"아이디: {user_id}"
        )
        lbl_review.config(
            text=f"⭐ 리뷰: {u.get('review_rate',0):.2f}/5 "
                 f"({u.get('review_count',0)}회)"
        )
        lbl_badge.config(text=f"🏅 뱃지: {u.get('badge','신규')}")
        lbl_penalty.config(text=f"⛔ 정지: {u.get('penalty',0)}일")
        lbl_done.config(text=f"✅ 완료: {u.get('cumulative_done',0)}회")
        lbl_cancel.config(text=f"❌ 취소: {u.get('cumulative_cancel',0)}회")

    update_labels(user)   # 첫 화면용

    # 4) 새로고침 함수 ---------------------------------------
    def refresh_info():
        update_user_status(user_id)           # 상태 재계산
        new_user = fetch_user()               # 최신 정보 재조회
        update_labels(new_user)

    # 5) 기능 버튼 -------------------------------------------
    tk.Button(
        win, text="📅 약속 관리", width=25,
        command=lambda: open_appointment_manager(user_id)
    ).pack(pady=8)

    tk.Button(
        win, text="🛒 거래 관리", width=25,
        command=lambda: open_transaction_manager(user_id)
    ).pack(pady=8)

    tk.Button(
        win, text="🔄 새로고침", width=25,
        command=refresh_info
    ).pack(pady=8)

    tk.Button(
        win, text="닫기", width=10,
        command=win.destroy
    ).pack(pady=20)


# ------------------ 테스트 실행 ---------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_mypage(user_id=70)
    root.mainloop()
