import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection
import random, string

def generate_transaction_id():
    chars = string.ascii_uppercase + string.digits
    while True:
        tid = ''.join(random.choices(chars, k=2))
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM Transaction WHERE transaction_id = %s",
                (tid,)
            )
            if cursor.fetchone()['cnt'] == 0:
                conn.close()
                return tid
        conn.close()

def open_appointment_list(user_id):
    win = tk.Toplevel()
    win.title("내가 대여자(렌더)인 약속 목록")
    win.geometry("700x500")

    listbox = tk.Listbox(win, width=100, height=15)
    listbox.pack(pady=10)

    details_text = tk.Text(win, height=8, width=100)
    details_text.pack(pady=5)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    accept_btn = tk.Button(btn_frame, text="✅ 수락")
    reject_btn = tk.Button(btn_frame, text="❌ 거절")
    accept_btn.pack_forget()
    reject_btn.pack_forget()

    appointments = []

    def safe_pack(w):  # helper
        if not w.winfo_ismapped():
            w.pack(side=tk.LEFT, padx=10)

    def safe_forget(w):
        if w.winfo_ismapped():
            w.pack_forget()

    # ----------------------------- refresh -------------------------------- #
    def refresh_appointments():
        nonlocal appointments
        listbox.delete(0, tk.END)
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT  a.appointment_id, a.post_id, a.borrower_id,
                            u.nickname          AS borrower_nickname,
                            a.rent_datetime, a.return_datetime,
                            a.rent_location, a.return_location,
                            a.appointment_state,
                            i.title            AS item_title     -- 🔄 Post·Item 조인으로 제목 가져오기
                    FROM appointment a
                    JOIN User  u  ON a.borrower_id = u.user_id
                    JOIN Post  p  ON a.post_id    = p.post_id
                    JOIN Item  i  ON p.item_id    = i.item_id
                    WHERE a.lender_id = %s
                      AND a.appointment_state = 'WAITING'
                    ORDER BY a.rent_datetime DESC
                """, (user_id,))
                appointments = cursor.fetchall()

                for app in appointments:
                    listbox.insert(
                        tk.END,
                        f"[{app['appointment_id']}] {app['item_title']} "
                        f"(post:{app['post_id']}) - borrower:{app['borrower_nickname']} "
                        f"- 상태:{app['appointment_state']}"
                    )
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn:
                conn.close()

        # 초기화
        safe_forget(accept_btn)
        safe_forget(reject_btn)
        details_text.delete("1.0", tk.END)

    # ----------------------------- update --------------------------------- #
    def update_appointment(appointment_id, new_state):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE appointment SET appointment_state = %s WHERE appointment_id = %s",
                    (new_state, appointment_id)
                )

                if new_state == 'CONFIRMED':
                    cursor.execute("""
                        SELECT lender_id, borrower_id, post_id
                        FROM appointment
                        WHERE appointment_id = %s
                    """, (appointment_id,))
                    appt = cursor.fetchone()

                    if appt:
                        tid = generate_transaction_id()
                        cursor.execute("""
                            INSERT INTO Transaction (
                                transaction_id, appointment_appointment_id,
                                lender_id, borrower_id, post_id,
                                transaction_state, rent_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        """, (
                            tid, appointment_id,
                            appt['lender_id'], appt['borrower_id'], appt['post_id'],
                            'Pending'          # 🔄 상태 값
                        ))
                        messagebox.showinfo("성공", "✅ 거래가 생성되었습니다.")

                conn.commit()
            messagebox.showinfo("성공", f"약속 상태가 '{new_state}' 로 변경되었습니다.")
            refresh_appointments()
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn:
                conn.close()

    # ----------------------------- select --------------------------------- #
    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            safe_forget(accept_btn)
            safe_forget(reject_btn)
            details_text.delete("1.0", tk.END)
            return

        app = appointments[sel[0]]
        details_text.delete("1.0", tk.END)
        details_text.insert(
            tk.END,
            f"약속 ID: {app['appointment_id']}\n"
            f"게시글 ID: {app['post_id']} ({app['item_title']})\n"
            f"borrower: {app['borrower_nickname']} (user_id: {app['borrower_id']})\n"
            f"대여 일시: {app['rent_datetime']}\n"
            f"반납 일시: {app['return_datetime']}\n"
            f"대여 장소: {app['rent_location']}\n"
            f"반납 장소: {app['return_location']}\n"
            f"상태: {app['appointment_state']}\n\n"
            "※ 상태가 WAITING일 때만 수락/거절 버튼이 보입니다."
        )

        if app['appointment_state'].strip().upper() == 'WAITING':
            accept_btn.config(
                command=lambda aid=app['appointment_id']: update_appointment(aid, 'CONFIRMED')
            )
            reject_btn.config(
                command=lambda aid=app['appointment_id']: update_appointment(aid, 'DECLINED')
            )
            safe_pack(accept_btn)
            safe_pack(reject_btn)
        else:
            safe_forget(accept_btn)
            safe_forget(reject_btn)

    listbox.bind('<<ListboxSelect>>', on_select)
    refresh_appointments()
