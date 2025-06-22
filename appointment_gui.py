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
                        'PENDING',0,1
                    )
                """, (
                    lender_id, borrower_id, post_id,
                    rent_dt, rent_location,
                    ret_dt, return_loc.get().strip(),
                    asked_price
                ))
                conn.commit()
            messagebox.showinfo("성공", "약속 제안 완료!")
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

