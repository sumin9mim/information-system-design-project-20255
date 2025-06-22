import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection
from post_gui import open_write_post
from post_list_gui import open_post_list
from mypage_gui import open_mypage

# --- 회원가입 함수 ---
def insert_user(email, nickname, profile_url, koruniv_verified):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "이미 등록된 이메일입니다."
            cursor.execute("""
                INSERT INTO User (email, nickname, profile_image_url, koruniv_verified)
                VALUES (%s, %s, %s, %s)
            """, (email, nickname, profile_url, koruniv_verified))
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID() AS user_id")
            user_id = cursor.fetchone()['user_id']
        conn.close()
        return True, (user_id, nickname)             # ✨ 닉네임도 같이 반환
    except Exception as e:
        return False, str(e)

# --- 로그인 함수 ---
def login_user(email):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, nickname, penalty         -- ✨ nickname 추가
                FROM User
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
        conn.close()
        if user:
            return True, (user['user_id'], user['nickname'], user['penalty'])  # ✨
        else:
            return False, "가입된 이메일이 없습니다."
    except Exception as e:
        return False, str(e)

# --- 회원가입 창 ---
def open_register_window():
    reg_win = tk.Toplevel()
    reg_win.title("회원가입")
    reg_win.geometry("500x350")

    tk.Label(reg_win, text="이메일").pack()
    email_entry = tk.Entry(reg_win, width=50)
    email_entry.pack()

    tk.Label(reg_win, text="닉네임").pack()
    nickname_entry = tk.Entry(reg_win, width=50)
    nickname_entry.pack()

    tk.Label(reg_win, text="프로필 이미지 URL").pack()
    profile_entry = tk.Entry(reg_win, width=50)
    profile_entry.pack()

    verified_var = tk.IntVar()
    tk.Checkbutton(reg_win, text="고려대 인증됨", variable=verified_var).pack()

    def on_register_click():
        email = email_entry.get()
        nickname = nickname_entry.get()
        profile_url = profile_entry.get()
        verified = 1 if verified_var.get() else 0

        if not email or not nickname:
            messagebox.showwarning("입력 오류", "이메일과 닉네임은 필수입니다.")
            return

        success, result = insert_user(email, nickname, profile_url, verified)
        if success:
            user_id, nickname = result            # ✨
            messagebox.showinfo("성공", "회원가입 완료!")
            reg_win.destroy()
            open_post_options_window(user_id, nickname)   # ✨ 닉네임 전달
        else:
            messagebox.showerror("실패", result)

    tk.Button(reg_win, text="회원가입 완료", command=on_register_click).pack(pady=20)

# --- 로그인 창 ---
def open_login_window():
    login_win = tk.Toplevel()
    login_win.title("로그인")
    login_win.geometry("400x200")

    tk.Label(login_win, text="이메일").pack()
    email_entry = tk.Entry(login_win, width=40)
    email_entry.pack()

    def on_login_click():
        email = email_entry.get()
        success, result = login_user(email)
        if success:
            user_id, nickname, penalty = result     # ✨
            if str(penalty) in ('3', '5'):
                messagebox.showwarning("이용 정지", f"{penalty}일 동안 이용이 정지되었습니다.")
                return
            messagebox.showinfo("로그인 성공", "환영합니다!")
            login_win.destroy()
            open_post_options_window(user_id, nickname)   # ✨
        else:
            messagebox.showerror("로그인 실패", result)

    tk.Button(login_win, text="로그인", command=on_login_click).pack(pady=15)

# --- 게시글 메뉴 ---
def open_post_options_window(user_id, nickname):      # ✨ 닉네임 인자 추가
    new_win = tk.Toplevel()
    new_win.title("게시글 메뉴")
    new_win.geometry("400x300")

    tk.Label(new_win,
             text=f"환영합니다, {nickname}님 (user id: {user_id})",  # ✨ 표시 형식
             pady=15).pack()

    tk.Button(new_win, text="📝 게시글 작성하기", width=25,
              command=lambda: open_write_post(user_id)).pack(pady=12)
    tk.Button(new_win, text="📋 게시글 목록 보기", width=25,
              command=lambda: open_post_list(user_id)).pack(pady=8)
    tk.Button(new_win, text="👤 마이페이지", width=25,
              command=lambda: open_mypage(user_id)).pack(pady=8)

# --- 메인 시작 화면 ---
if __name__ == '__main__':
    root = tk.Tk()
    root.title("레플레카 대여 시스템")
    root.geometry("400x250")

    tk.Button(root, text="회원가입", width=25, command=open_register_window).pack(pady=25)
    tk.Button(root, text="로그인",   width=25, command=open_login_window).pack(pady=25)

    root.mainloop()
