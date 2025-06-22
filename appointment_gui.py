import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from db_connect import get_connection
from datetime import date

# ────────────────────────────────────────────────
# 1) 약속(appointment) 등록 폼
# ────────────────────────────────────────────────
def open_appointment_form(user_id, post_id):
    # ── 게시글 정보 가져오기 ─────────────────────────────
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT user_id AS lender_id, location, price
            FROM Post WHERE post_id = %s
        """, (post_id,))
        post = cur.fetchone()
    conn.close()

    if not post:
        messagebox.showerror("에러", "게시글 정보를 찾을 수 없습니다.")
        return

    lender_id     = post['lender_id']
    borrower_id   = user_id
    rent_location = post['location']
    asked_price   = post['price']

    win = tk.Toplevel()
    win.title("약속 등록")
    win.geometry("420x520")

    today = date.today()
    years  = [str(y) for y in range(today.year, today.year + 3)]
    months = [f"{m:02d}" for m in range(1, 13)]
    days   = [f"{d:02d}" for d in range(1, 32)]

    # ── 대여 날짜 (년·월·일) ───────────────────────────
    tk.Label(win, text="대여 날짜").pack()
    f_rent_date = tk.Frame(win); f_rent_date.pack()
    rent_y = ttk.Combobox(f_rent_date, values=years,  width=5, state='readonly'); rent_y.set(years[0])
    rent_m = ttk.Combobox(f_rent_date, values=months, width=3, state='readonly'); rent_m.set(months[today.month-1])
    rent_d = ttk.Combobox(f_rent_date, values=days,   width=3, state='readonly'); rent_d.set(days[today.day-1])
    for w,t in ((rent_y,"년"),(rent_m,"월"),(rent_d,"일")):
        w.pack(side=tk.LEFT); tk.Label(f_rent_date, text=t).pack(side=tk.LEFT)

    # ── 대여 시간 (시·분) ────────────────────────────
    tk.Label(win, text="대여 시간 (HH:MM)").pack()
    f_rent_time = tk.Frame(win); f_rent_time.pack()
    rent_h = ttk.Combobox(f_rent_time, values=[f"{i:02d}" for i in range(24)],
                          width=3, state='readonly'); rent_h.set("00")
    rent_mi = ttk.Combobox(f_rent_time, values=[f"{i:02d}" for i in range(60)],
                           width=3, state='readonly'); rent_mi.set("00")
    rent_h.pack(side=tk.LEFT); tk.Label(f_rent_time, text=":").pack(side=tk.LEFT); rent_mi.pack(side=tk.LEFT)

    # ── 반납 날짜 (년·월·일) ──────────────────────────
    tk.Label(win, text="반납 날짜").pack()
    f_ret_date = tk.Frame(win); f_ret_date.pack()
    ret_y = ttk.Combobox(f_ret_date, values=years,  width=5, state='readonly'); ret_y.set(years[0])
    ret_m = ttk.Combobox(f_ret_date, values=months, width=3, state='readonly'); ret_m.set(months[today.month-1])
    ret_d = ttk.Combobox(f_ret_date, values=days,   width=3, state='readonly'); ret_d.set(days[today.day-1])
    for w,t in ((ret_y,"년"),(ret_m,"월"),(ret_d,"일")):
        w.pack(side=tk.LEFT); tk.Label(f_ret_date, text=t).pack(side=tk.LEFT)

    # ── 반납 시간 (시·분) ────────────────────────────
    tk.Label(win, text="반납 시간 (HH:MM)").pack()
    f_ret_time = tk.Frame(win); f_ret_time.pack()
    ret_h = ttk.Combobox(f_ret_time, values=[f"{i:02d}" for i in range(24)],
                         width=3, state='readonly'); ret_h.set("00")
    ret_mi = ttk.Combobox(f_ret_time, values=[f"{i:02d}" for i in range(60)],
                          width=3, state='readonly'); ret_mi.set("00")
    ret_h.pack(side=tk.LEFT); tk.Label(f_ret_time, text=":").pack(side=tk.LEFT); ret_mi.pack(side=tk.LEFT)

    # ── 반납 장소 ───────────────────────────────────
    tk.Label(win, text="반납 장소").pack()
    return_loc = tk.Entry(win, width=42); return_loc.pack()

    # ── 등록 버튼 ───────────────────────────────────
    def register():
        if not return_loc.get().strip():
            messagebox.showwarning("입력 오류", "반납 장소를 입력해주세요.")
            return

        rent_dt = f"{rent_y.get()}-{rent_m.get()}-{rent_d.get()} {rent_h.get()}:{rent_mi.get()}:00"
        ret_dt  = f"{ret_y.get()}-{ret_m.get()}-{ret_d.get()} {ret_h.get()}:{ret_mi.get()}:00"

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO appointment (
                        lender_id, borrower_id, post_id,
                        rent_datetime, rent_location,
                        return_datetime, return_location,
                        asked_price, appointment_state,
                        lender_confirm, borrower_confirm
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,
                        'WAITING',0,0
                    )
                """, (
                    lender_id, borrower_id, post_id,
                    rent_dt, rent_location,
                    ret_dt, return_loc.get().strip(),
                    asked_price
                ))
                conn.commit()
            messagebox.showinfo("성공", "약속 등록 완료!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn:
                conn.close()

    tk.Button(win, text="약속 등록", command=register).pack(pady=25)

# ────────────────────────────────────────────────
# ────────────────────────────────────────────────
# 2) 대여자(렌더) 입장에서 보는 약속 목록  🔄 제목 표시 추가
# ────────────────────────────────────────────────
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
                    SELECT  a.appointment_id,
                            a.post_id,
                            i.title        AS item_title,      -- 🔄
                            u.nickname     AS borrower_nickname,
                            a.rent_datetime, a.return_datetime,
                            a.rent_location, a.return_location,
                            a.appointment_state
                    FROM appointment a
                    JOIN User  u ON a.borrower_id = u.user_id
                    JOIN Post  p ON a.post_id     = p.post_id    -- 🔄
                    JOIN Item  i ON p.item_id     = i.item_id    -- 🔄
                    WHERE a.lender_id = %s
                    ORDER BY a.rent_datetime DESC
                """, (user_id,))
                appointments = cursor.fetchall()

                for app in appointments:
                    listbox.insert(
                        tk.END,
                        f"[{app['appointment_id']}] {app['item_title']} "
                        f"(post:{app['post_id']}) - "
                        f"요청자:{app['borrower_nickname']} - "
                        f"상태:{app['appointment_state']}"
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
        details_text.insert(
            tk.END,
            f"약속 ID   : {app['appointment_id']}\n"
            f"게시글 ID : {app['post_id']} ({app['item_title']})\n"  # 🔄
            f"대여자    : 본인 (user_id={user_id})\n"
            f"대여 일시 : {app['rent_datetime']}\n"
            f"반납 일시 : {app['return_datetime']}\n"
            f"대여 장소 : {app['rent_location']}\n"
            f"반납 장소 : {app['return_location']}\n"
            f"상태      : {app['appointment_state']}\n\n"
            "※ 상태가 WAITING일 때만 수락/거절 버튼 활성화됩니다."
        )

        if app['appointment_state'] == 'WAITING':
            accept_btn.config(state=tk.NORMAL)
            reject_btn.config(state=tk.NORMAL)
        else:
            accept_btn.config(state=tk.DISABLED)
            reject_btn.config(state=tk.DISABLED)

        accept_btn.config(
            command=lambda: update_appointment(app['appointment_id'], 'ACCEPTED')
        )
        reject_btn.config(
            command=lambda: update_appointment(app['appointment_id'], 'REJECTED')
        )

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

    listbox.bind("<<ListboxSelect>>", on_select)
    refresh_appointments()
