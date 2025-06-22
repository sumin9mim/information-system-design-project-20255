import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection

def open_borrowed_appointment_list(user_id):
    win = tk.Toplevel()
    win.title("내가 요청자로 제안한 약속 목록")
    win.geometry("700x500")

    listbox = tk.Listbox(win, width=100, height=20)
    listbox.pack(pady=10)

    details_text = tk.Text(win, height=10, width=100)
    details_text.pack(pady=5)

    appointments = []

    def refresh_appointments():
        nonlocal appointments
        listbox.delete(0, tk.END)
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT  a.appointment_id,
                            a.post_id,
                            i.title        AS item_title,          -- 🔄
                            u.nickname     AS lender_nickname,
                            a.rent_datetime, a.return_datetime,
                            a.rent_location, a.return_location,
                            a.appointment_state, i.product_type, i.size
                    FROM appointment a
                    JOIN User  u ON a.lender_id = u.user_id
                    JOIN Post  p ON a.post_id   = p.post_id      -- 🔄
                    JOIN Item  i ON p.item_id   = i.item_id      -- 🔄
                    WHERE a.borrower_id = %s
                    ORDER BY a.rent_datetime DESC
                """, (user_id,))
                appointments = cursor.fetchall()

                for app in appointments:
                    listbox.insert(
                        tk.END,
                        f"[{app['appointment_id']}]{app['item_title']}"
                        f"제품:{app['product_type']}"
                        f"대여자:{app['lender_nickname']} - "
                        f"상태:{app['appointment_state']}"
                    )
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn:
                conn.close()

        details_text.delete("1.0", tk.END)

    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            details_text.delete("1.0", tk.END)
            return
        app = appointments[sel[0]]

        details_text.delete("1.0", tk.END)
        details_text.insert(
            tk.END,
            f"약속 ID   : {app['appointment_id']}\n"
            f"게시글: {app['item_title']} (post{app['post_id']})\n" 
            f"제품: {app['product_type']}({app['size']})\n"
            f"대여자    : {app['lender_nickname']}\n"
            f"대여 일시 : {app['rent_datetime']}\n"
            f"반납 일시 : {app['return_datetime']}\n"
            f"대여 장소 : {app['rent_location']}\n"
            f"반납 장소 : {app['return_location']}\n"
            f"약속 상태 : {app['appointment_state']}"
        )

    listbox.bind('<<ListboxSelect>>', on_select)
    refresh_appointments()
