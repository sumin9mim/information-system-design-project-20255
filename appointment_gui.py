import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from db_connect import get_connection

def open_appointment_form(user_id, post_id):
    # DB에서 게시글 정보 조회
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT user_id AS lender_id, location, price
            FROM Post
            WHERE post_id = %s
        """, (post_id,))
        post = cursor.fetchone()
    conn.close()

    if not post:
        messagebox.showerror("에러", "게시글 정보를 찾을 수 없습니다.")
        return

    borrower_id = user_id
    lender_id = post['lender_id']
    rent_location = post['location']
    asked_price = post['price']

    win = tk.Toplevel()
    win.title("약속 등록")
    win.geometry("400x500")

    tk.Label(win, text="대여 날짜 선택").pack()
    rent_date = DateEntry(win, date_pattern='yyyy-MM-dd')
    rent_date.pack()

    tk.Label(win, text="대여 시간 (HH:MM:SS)").pack()
    frame_rent_time = tk.Frame(win)
    frame_rent_time.pack()
    rent_hour = ttk.Combobox(frame_rent_time, values=[f"{i:02d}" for i in range(24)], width=3)
    rent_minute = ttk.Combobox(frame_rent_time, values=[f"{i:02d}" for i in range(60)], width=3)
    rent_second = ttk.Combobox(frame_rent_time, values=[f"{i:02d}" for i in range(60)], width=3)
    rent_hour.pack(side=tk.LEFT, padx=2)
    rent_minute.pack(side=tk.LEFT, padx=2)
    rent_second.pack(side=tk.LEFT, padx=2)

    tk.Label(win, text="반납 날짜 선택").pack()
    return_date = DateEntry(win, date_pattern='yyyy-MM-dd')
    return_date.pack()

    tk.Label(win, text="반납 시간 (HH:MM:SS)").pack()
    frame_return_time = tk.Frame(win)
    frame_return_time.pack()
    return_hour = ttk.Combobox(frame_return_time, values=[f"{i:02d}" for i in range(24)], width=3)
    return_minute = ttk.Combobox(frame_return_time, values=[f"{i:02d}" for i in range(60)], width=3)
    return_second = ttk.Combobox(frame_return_time, values=[f"{i:02d}" for i in range(60)], width=3)
    return_hour.pack(side=tk.LEFT, padx=2)
    return_minute.pack(side=tk.LEFT, padx=2)
    return_second.pack(side=tk.LEFT, padx=2)

    tk.Label(win, text="반납 장소").pack()
    return_loc = tk.Entry(win, width=40)
    return_loc.pack()

    def register():
        rent_dt = f"{rent_date.get()} {rent_hour.get()}:{rent_minute.get()}:{rent_second.get()}"
        return_dt = f"{return_date.get()} {return_hour.get()}:{return_minute.get()}:{return_second.get()}"
        return_loc_val = return_loc.get()

        if not all([rent_hour.get(), rent_minute.get(), rent_second.get(),
                    return_hour.get(), return_minute.get(), return_second.get(),
                    return_loc_val]):
            messagebox.showwarning("입력 오류", "시간 및 장소를 모두 입력해주세요.")
            return

        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO appointment (
                        lender_id, borrower_id, post_id,
                        rent_datetime, rent_location,
                        return_datetime, return_location,
                        asked_price, appointment_state,
                        lender_confirm, borrower_confirm
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'WAITING', 0, 0)
                """, (
                    lender_id, borrower_id, post_id,
                    rent_dt, rent_location,
                    return_dt, return_loc_val,
                    asked_price
                ))
                conn.commit()
            messagebox.showinfo("성공", "약속 등록 완료")
            win.destroy()
        except Exception as e:
            messagebox.showerror("오류", str(e))
        finally:
            if conn:
                conn.close()

    tk.Button(win, text="약속 등록", command=register).pack(pady=15)
import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection

def open_appointment_list(user_id):
    win = tk.Toplevel()
    win.title("내가 대여자(렌더)인 약속 목록")
    win.geometry("700x450")

    listbox = tk.Listbox(win, width=100, height=20)
    listbox.pack(pady=10)

    details_text = tk.Text(win, height=10, width=100)
    details_text.pack()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    accept_btn = tk.Button(btn_frame, text="✅ 수락", state=tk.DISABLED)
    reject_btn = tk.Button(btn_frame, text="❌ 거절", state=tk.DISABLED)
    accept_btn.pack(side=tk.LEFT, padx=10)
    reject_btn.pack(side=tk.LEFT, padx=10)

    appointments = []

    def refresh_appointments():
        nonlocal appointments
        listbox.delete(0, tk.END)
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT a.appointment_id, a.post_id, u.nickname AS borrower_nickname,
                           a.rent_datetime, a.return_datetime, a.rent_location, a.return_location,
                           a.appointment_state
                    FROM appointment a
                    JOIN User u ON a.borrower_id = u.user_id
                    WHERE a.lender_id = %s
                    ORDER BY a.rent_datetime DESC
                """, (user_id,))
                appointments = cursor.fetchall()

                for app in appointments:
                    listbox.insert(tk.END,
                        f"[{app['appointment_id']}] 게시글ID:{app['post_id']} - 대여자:{app['borrower_nickname']} - 상태:{app['appointment_state']}"
                    )
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn:
                conn.close()

        accept_btn.config(state=tk.DISABLED)
        reject_btn.config(state=tk.DISABLED)
        details_text.delete("1.0", tk.END)

    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            return
        app = appointments[sel[0]]

        details_text.delete("1.0", tk.END)
        details_text.insert(tk.END,
            f"약속 ID: {app['appointment_id']}\n"
            f"게시글 ID: {app['post_id']}\n"
            f"대여자: 본인 (user_id={user_id})\n"
            f"대여 일시: {app['rent_datetime']}\n"
            f"반납 일시: {app['return_datetime']}\n"
            f"대여 장소: {app['rent_location']}\n"
            f"반납 장소: {app['return_location']}\n"
            f"상태: {app['appointment_state']}\n\n"
            "※ 상태가 WAITING일 때만 수락/거절 버튼 활성화됩니다."
        )

        if app['appointment_state'] == 'WAITING':
            accept_btn.config(state=tk.NORMAL)
            reject_btn.config(state=tk.NORMAL)
        else:
            accept_btn.config(state=tk.DISABLED)
            reject_btn.config(state=tk.DISABLED)

        accept_btn.config(command=lambda: update_appointment(app['appointment_id'], 'ACCEPTED'))
        reject_btn.config(command=lambda: update_appointment(app['appointment_id'], 'REJECTED'))

    def update_appointment(appointment_id, new_state):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE appointment
                    SET appointment_state = %s
                    WHERE appointment_id = %s
                """, (new_state, appointment_id))
                conn.commit()
            messagebox.showinfo("성공", f"약속이 '{new_state}' 상태로 변경되었습니다.")
            refresh_appointments()
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn:
                conn.close()

    listbox.bind('<<ListboxSelect>>', on_select)

    refresh_appointments()
