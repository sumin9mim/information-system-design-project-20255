import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection
from appointment_gui import open_appointment_form  # 약속 폼 열기 함수

def open_post_list(user_id):
    """
    user_id: 현재 로그인한 사용자의 ID
    """
    win = tk.Toplevel()
    win.title("📋 게시글 목록")
    win.geometry("600x600")

    # 게시글 리스트박스
    listbox = tk.Listbox(win, width=80, height=15)
    listbox.pack(pady=10)

    # 상세 정보 표시용 텍스트
    detail_text = tk.Text(win, height=8, width=80)
    detail_text.pack(pady=5)

    # 약속하기 버튼 (선택 시 표시)
    appoint_btn = tk.Button(win, text="📅 약속하기", command=lambda: None)
    appoint_btn.pack_forget()

    # DB에서 게시글 조회 (Pending/Confirmed 상태의 transaction 걸려있는 글 제외)
    posts = []
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.post_id, p.user_id, u.nickname, i.title, p.price, p.location, i.description
                FROM Post p
                JOIN User   u ON p.user_id = u.user_id
                JOIN Item   i ON p.item_id = i.item_id
                WHERE p.post_id NOT IN (
                    SELECT t.post_id
                    FROM `Transaction` t
                    WHERE t.transaction_state IN ('Pending','Confirmed')
                )
                ORDER BY p.post_id DESC
            """)
            posts = cursor.fetchall()

            for post in posts:
                label = "(내 게시글)" if post['user_id'] == user_id else ""
                listbox.insert(
                    tk.END,
                    f"[{post['post_id']}] {post['title']} - {post['nickname']} {label}"
                )
    except Exception as e:
        messagebox.showerror("DB 오류", str(e))
    finally:
        if conn:
            conn.close()

    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            return
        post = posts[sel[0]]

        # 상세 정보 표시
        detail_text.delete("1.0", tk.END)
        detail_text.insert(tk.END,
            f"🆔 게시글 ID: {post['post_id']}\n"
            f"👤 작성자 닉네임: {post['nickname']}\n"
            f"📌 제목: {post['title']}\n"
            f"💸 가격: {post['price']}원\n"
            f"📍 위치: {post['location']}\n"
            f"📝 설명: {post['description']}"
        )

        # 내가 쓴 글이면 약속 버튼 숨김
        if post['user_id'] == user_id:
            appoint_btn.pack_forget()
            messagebox.showinfo("알림", "이 글은 내가 작성한 게시글입니다.")
        else:
            # 약속 폼 열기
            appoint_btn.config(
                command=lambda pid=post['post_id']: open_appointment_form(user_id, pid)
            )
            appoint_btn.pack(pady=5)

    # 리스트 선택 이벤트 바인딩
    listbox.bind('<<ListboxSelect>>', on_select)

# — 아래는 예시로 메인 윈도우에서 호출하는 부분 —
if __name__ == "__main__":
    def dummy_login():
        # 실제로는 로그인 처리 후 user_id를 넘겨야 합니다.
        return 1

    root = tk.Tk()
    root.title("메인 창")
    root.geometry("300x200")

    btn = tk.Button(root, text="게시글 목록 열기", command=lambda: open_post_list(dummy_login()))
    btn.pack(expand=True)

    root.mainloop()
