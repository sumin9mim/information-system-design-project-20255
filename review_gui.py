import tkinter as tk
from tkinter import messagebox
from db_connect import get_connection

def open_review_form(transaction_id, reviewer_id, reviewee_id, on_complete=None):
    win = tk.Toplevel()
    win.title("리뷰 작성")
    win.geometry("400x300")

    tk.Label(win, text="평점을 입력해주세요 (1~5):").pack(pady=5)
    rating_entry = tk.Entry(win)
    rating_entry.pack(pady=5)

    def submit_review():
        try:
            rating = int(rating_entry.get())
            if rating < 1 or rating > 5:
                raise ValueError("1~5 사이의 정수를 입력해주세요.")

            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE User
                    SET review_sum = review_sum + %s,
                        review_count = review_count + 1,
                        review_rate = (review_sum + %s) / (review_count + 1)
                    WHERE user_id = %s
                """, (rating, rating, reviewee_id))
                conn.commit()

            messagebox.showinfo("리뷰 완료", "리뷰가 성공적으로 등록되었습니다.")
            if on_complete:
                on_complete()
            win.destroy()
        except Exception as e:
            messagebox.showerror("오류", str(e))
        finally:
            if conn:
                conn.close()

    tk.Button(win, text="리뷰 제출", command=submit_review).pack(pady=10)