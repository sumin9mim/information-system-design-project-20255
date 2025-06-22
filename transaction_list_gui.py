import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection
from review_gui import open_review_form

def open_transaction_list(user_id):
    win = tk.Toplevel()
    win.title("⏳ 진행 중인 거래")
    win.geometry("800x600")

    listbox = tk.Listbox(win, width=120, height=20); listbox.pack(pady=10)
    details_text = tk.Text(win, height=12, width=120); details_text.pack(pady=5)

    btn_frame = tk.Frame(win); btn_frame.pack(pady=10)
    accept_btn = tk.Button(btn_frame, text="✅ 거래 완료")
    cancel_btn = tk.Button(btn_frame, text="❌ 거래 취소")
    accept_btn.pack_forget(); cancel_btn.pack_forget()

    transactions = []

    # helpers
    safe_pack   = lambda w: w.pack(side=tk.LEFT, padx=10) if not w.winfo_ismapped() else None
    safe_forget = lambda w: w.pack_forget()               if w.winfo_ismapped()    else None

    # ────────────── 목록 새로고침 ──────────────
    def refresh():
        nonlocal transactions
        listbox.delete(0, tk.END)
        safe_forget(accept_btn); safe_forget(cancel_btn)
        details_text.delete("1.0", tk.END)

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT  t.transaction_id, t.post_id,
                            t.lender_id, t.borrower_id,
                            t.transaction_state,
                            t.lender_confirm, t.borrower_confirm,
                            t.rent_at,
                            u1.nickname AS lender_nickname,
                            u2.nickname AS borrower_nickname,
                            i.title      AS title,
                            i.product_type, i.size
                    FROM  `Transaction` t
                    LEFT  JOIN `User` u1 ON t.lender_id   = u1.user_id
                    LEFT  JOIN `User` u2 ON t.borrower_id = u2.user_id
                    JOIN  Post  p ON t.post_id = p.post_id
                    JOIN  Item  i ON p.item_id = i.item_id
                    WHERE UPPER(t.transaction_state) = 'PENDING'            -- ← 대소문자 무시
                      AND (t.lender_id = %s OR t.borrower_id = %s)
                    ORDER BY t.rent_at DESC
                """, (user_id, user_id))
                transactions = cur.fetchall()

            for tr in transactions:
                listbox.insert(
                    tk.END,
                    f"[{tr['transaction_id']}] {tr['title']} "
                    f"(post:{tr['post_id']}) - "
                    f"대여자:{tr['lender_nickname']} / "
                    f"요청자:{tr['borrower_nickname']} - "
                    f"상태:{tr['transaction_state']}"
                )
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn: conn.close()

    # ────────────── 수락/취소 처리 ──────────────
    def update_confirmation(txid, role, action):
        """
        role   : 'lender' | 'borrower'
        action : 'ACCEPT' | 'CANCEL'
        """
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # ① 클릭 기록
                val = 1 if action == 'ACCEPT' else -1
                cur.execute(
                    f"UPDATE `Transaction` SET {role}_confirm=%s WHERE transaction_id=%s",
                    (val, txid)
                )

                # ② 현재 확인 상태
                cur.execute("""
                    SELECT lender_confirm, borrower_confirm,
                           lender_id, borrower_id, cancelled_by
                    FROM   `Transaction`
                    WHERE  transaction_id=%s
                """, (txid,))
                conf = cur.fetchone()

                # ③ 상태·누적 카운트
                if action == 'CANCEL':
                    # 취소자 첫 기록이면 누적 +1
                    if conf['cancelled_by'] is None:
                        cur.execute("""
                            UPDATE User
                            SET cumulative_cancel = cumulative_cancel + 1
                            WHERE user_id = %s
                        """, (user_id,))

                    cur.execute("""
                        UPDATE `Transaction`
                        SET transaction_state = 'CANCELLED',
                            cancelled_by     = %s
                        WHERE transaction_id = %s
                    """, (user_id, txid))

                    msg = "거래를 취소하였습니다.\n거래가 최종 취소됩니다."

                else:  # ACCEPT
                    if conf['lender_confirm'] == 1 and conf['borrower_confirm'] == 1:
                        cur.execute("""
                            UPDATE `Transaction`
                            SET transaction_state = 'CONFIRMED',
                                returned_at      = NOW()
                            WHERE transaction_id = %s
                        """, (txid,))
                        cur.execute("""
                            UPDATE User
                            SET cumulative_done = cumulative_done + 1
                            WHERE user_id IN (%s, %s)
                        """, (conf['lender_id'], conf['borrower_id']))
                        msg = "거래가 최종 완료되었습니다."
                    else:
                        msg = "거래 완료 버튼을 눌렀습니다.\n상대방의 확인을 기다립니다."

                conn.commit()

            messagebox.showinfo("알림", msg)
            refresh()

        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            if conn: conn.close()

    # ────────────── 리스트 선택 ──────────────
    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            safe_forget(accept_btn); safe_forget(cancel_btn)
            details_text.delete("1.0", tk.END)
            return

        tr = transactions[sel[0]]

        details_text.delete("1.0", tk.END)
        details_text.insert(
            tk.END,
            f"거래 ID         : {tr['transaction_id']}\n"
            f"게시글          : {tr['title']} (post{tr['post_id']})\n"
            f"제품종류(사이즈): {tr['product_type']} ({tr['size']})\n"
            f"대여자          : {tr['lender_nickname']}\n"
            f"요청자          : {tr['borrower_nickname']}\n"
            f"거래상태        : {tr['transaction_state']}\n"
            f"대여일          : {tr['rent_at']}\n"
            f"대여자 확인     : {tr['lender_confirm']}\n"
            f"요청자 확인     : {tr['borrower_confirm']}"
        )

        if tr['transaction_state'].upper() == 'PENDING':
            role = 'lender' if user_id == tr['lender_id'] else 'borrower'
            accept_btn.config(
                command=lambda tid=tr['transaction_id'], r=role:
                    update_confirmation(tid, r, 'ACCEPT')
            )
            cancel_btn.config(
                command=lambda tid=tr['transaction_id'], r=role:
                    update_confirmation(tid, r, 'CANCEL')
            )
            safe_pack(accept_btn); safe_pack(cancel_btn)
        else:
            safe_forget(accept_btn); safe_forget(cancel_btn)

    # 초기 바인딩 & 로딩
    listbox.bind('<<ListboxSelect>>', on_select)
    refresh()


# ✅ 내가 취소한 거래 목록
def open_cancelled_transaction_list(user_id):
    win = tk.Toplevel()
    win.title("❌ 내가 취소한 거래 목록")
    win.geometry("800x600")

    listbox = tk.Listbox(win, width=120, height=25)
    listbox.pack(pady=10)

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.transaction_id, t.post_id, t.lender_id, t.borrower_id,
                       t.rent_at, t.returned_at,
                       u1.nickname AS lender_nickname,
                       u2.nickname AS borrower_nickname,
                       i.title     AS item_title             -- 🔄 제목
                FROM Transaction t
                LEFT JOIN User  u1 ON t.lender_id  = u1.user_id
                LEFT JOIN User  u2 ON t.borrower_id = u2.user_id
                JOIN Post  p ON t.post_id = p.post_id
                JOIN Item  i ON p.item_id = i.item_id
                WHERE t.transaction_state = 'Cancelled'
                  AND t.cancelled_by = %s
                ORDER BY t.rent_at DESC
            """, (user_id,))
            cancelled = cursor.fetchall()

            for tr in cancelled:
                listbox.insert(
                    tk.END,
                    f"[거래ID: {tr['transaction_id']}]{tr['item_title']}"
                    f"[- 대여자:{tr['lender_nickname']} / 요청자:{tr['borrower_nickname']}]"
                    f", post: {tr['item_title']}"
                    f", 대여예정일:{tr['rent_at']}"
                )
    except Exception as e:
        messagebox.showerror("DB 오류", str(e))
    finally:
        if conn:
            conn.close()

# — 상대방이 취소한 거래 목록 —
def open_other_cancelled_transaction_list(user_id):
    win = tk.Toplevel()
    win.title("🚫 상대방이 취소한 거래")
    win.geometry("800x600")

    lb = tk.Listbox(win, width=120, height=25)
    lb.pack(pady=10)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.transaction_id, t.post_id, t.rent_at, t.returned_at,
                       t.lender_id, t.borrower_id, t.cancelled_by,
                       u1.nickname AS lender, u2.nickname AS borrower,
                       i.title     AS item_title             -- 🔄 제목
                FROM `Transaction` t
                LEFT JOIN `User` u1 ON t.lender_id  = u1.user_id
                LEFT JOIN `User` u2 ON t.borrower_id = u2.user_id
                JOIN  Post  p ON t.post_id = p.post_id
                JOIN  Item  i ON p.item_id = i.item_id
                WHERE t.transaction_state = 'Cancelled'
                  AND t.cancelled_by != %s
                  AND (t.lender_id = %s OR t.borrower_id = %s)
                ORDER BY t.rent_at DESC
            """, (user_id, user_id, user_id))
            rows = cur.fetchall()

            if not rows:
                lb.insert(tk.END, "상대방이 취소한 거래가 없습니다.")
            else:
                for tr in rows:
                    by_role = '대여자' if tr['cancelled_by'] == tr['lender_id'] else '요청자'
                    by_name = tr['lender'] if by_role == '대여자' else tr['borrower']
                    lb.insert(
                        tk.END,
                        f"취소자({by_role}):{by_name} "
                        f"[거래ID: {tr['transaction_id']}]{tr['item_title']}"
                        f", 대여예정일:{tr['rent_at']}"
                    )
    finally:
        conn.close()

# ✅ 완료된 거래 목록
def open_confirmed_transaction_list(user_id):
    win = tk.Toplevel()
    win.title("✅ 완료된 거래 목록")
    win.geometry("800x600")

    listbox = tk.Listbox(win, width=120, height=20)
    listbox.pack(pady=10)

    review_btn = tk.Button(win, text="📝 리뷰 쓰기")
    review_btn.pack_forget()

    confirmed = []

    def refresh():
        nonlocal confirmed
        listbox.delete(0, tk.END)
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.transaction_id, t.post_id, t.lender_id, t.borrower_id,
                           t.rent_at, t.returned_at,
                           u1.nickname AS lender_nickname,
                           u2.nickname AS borrower_nickname,
                           i.title     AS item_title           -- 🔄 제목
                    FROM `Transaction` t
                    LEFT JOIN `User` u1 ON t.lender_id  = u1.user_id
                    LEFT JOIN `User` u2 ON t.borrower_id = u2.user_id
                    JOIN  Post  p ON t.post_id = p.post_id
                    JOIN  Item  i ON p.item_id = i.item_id
                    WHERE t.transaction_state = 'Confirmed'
                      AND (t.lender_id = %s OR t.borrower_id = %s)
                    ORDER BY t.rent_at DESC
                """, (user_id, user_id))
                confirmed = cursor.fetchall()
                for tr in confirmed:
                    listbox.insert(
                        tk.END,
                        f"[{tr['transaction_id']}] {tr['item_title']} "
                        f"(post:{tr['post_id']}) - "
                        f"lender:{tr['lender_nickname']} / borrower:{tr['borrower_nickname']} "
                        f"- 대여일:{tr['rent_at']} / 반납일:{tr['returned_at'] or '미완료'}"
                    )
        except Exception as e:
            messagebox.showerror("DB 오류", str(e))
        finally:
            conn.close()

    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            review_btn.pack_forget()
            return
        tr = confirmed[sel[0]]
        reviewee_id = tr['lender_id'] if user_id == tr['borrower_id'] else tr['borrower_id']
        review_btn.config(
            state="normal",
            command=lambda: open_review_form(
                tr['transaction_id'], user_id, reviewee_id,
                on_complete=lambda: review_btn.config(text='✅ 작성 완료', state='disabled')
            )
        )
        review_btn.pack(pady=10)

    listbox.bind("<<ListboxSelect>>", on_select)
    refresh()

# — 만료된 거래 목록 —
def open_expired_transaction_list(user_id):
    win = tk.Toplevel()
    win.title("⏰ 만료된 거래")
    win.geometry("800x600")
    lb = tk.Listbox(win, width=120, height=25)
    lb.pack(pady=10)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.transaction_id, t.post_id, t.rent_at,
                       u1.nickname AS lender, u2.nickname AS borrower,
                       i.title     AS item_title           -- 🔄 제목
                FROM `Transaction` t
                LEFT JOIN `User` u1 ON t.lender_id  = u1.user_id
                LEFT JOIN `User` u2 ON t.borrower_id = u2.user_id
                JOIN  Post  p ON t.post_id = p.post_id
                JOIN  Item  i ON p.item_id = i.item_id
                WHERE t.transaction_state = 'Expired'
                  AND (t.lender_id = %s OR t.borrower_id = %s)
                ORDER BY t.rent_at DESC
            """, (user_id, user_id))
            for tr in cur.fetchall():
                lb.insert(
                    tk.END,
                    f"[{tr['transaction_id']}] {tr['item_title']} "
                    f"({tr['lender']} / {tr['borrower']} "
                    f"({tr['rent_at']})"
                )
    finally:
        conn.close()

# — 메인 윈도우 예시 —
if __name__ == "__main__":
    def dummy_login():
        return 1  # 실제 로그인 로직으로 교체

    root = tk.Tk()
    root.title("거래 대시보드")
    root.geometry("300x400")
    uid = dummy_login()

    buttons = [
        ("진행 중 거래", lambda: open_transaction_list(uid)),
        ("내가 취소한 거래", lambda: open_cancelled_transaction_list(uid)),
        ("상대방이 취소한 거래", lambda: open_other_cancelled_transaction_list(uid)),
        ("만료된 거래", lambda: open_expired_transaction_list(uid)),
    ]
    for txt, cmd in buttons:
        tk.Button(root, text=txt, width=25, command=cmd).pack(pady=5)

    root.mainloop()
