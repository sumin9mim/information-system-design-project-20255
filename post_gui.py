import tkinter as tk
from tkinter import messagebox, ttk
from db_connect import get_connection  # DB 연결 함수

def open_write_post(user_email):
    win = tk.Toplevel()
    win.title("📝 게시글 작성하기")
    win.geometry("500x600")

    # --- UI 입력 필드 ---
    tk.Label(win, text="제목").pack()
    title_entry = tk.Entry(win, width=50)
    title_entry.pack()

    tk.Label(win, text="설명").pack()
    desc_text = tk.Text(win, height=4, width=50)
    desc_text.pack()

    tk.Label(win, text="가격").pack()
    price_entry = tk.Entry(win)
    price_entry.pack()

    tk.Label(win, text="거래장소").pack()
    location_entry = tk.Entry(win)
    location_entry.pack()

    tk.Label(win, text="상품 유형").pack()
    product_type_combo = ttk.Combobox(win, values=["하키복", "농구조끼", "티셔츠", "야구점퍼"])
    product_type_combo.pack()

    tk.Label(win, text="사이즈").pack()
    size_combo = ttk.Combobox(win, values=["SMALL", "MEDIUM", "LARGE"])  # DB enum 값에 맞게
    size_combo.pack()

    tk.Label(win, text="이미지 URL").pack()
    image_entry = tk.Entry(win, width=50)
    image_entry.pack()

    # --- 등록 로직 ---
    def submit_post():
        title = title_entry.get()
        description = desc_text.get("1.0", "end").strip()
        price = price_entry.get()
        location = location_entry.get()
        product_type = product_type_combo.get()
        size = size_combo.get()
        image_url = image_entry.get()

        # 입력 필수 체크
        if not all([title, description, price, location, product_type, size]):
            messagebox.showwarning("입력 오류", "모든 항목을 입력해주세요.")
            return

        # 가격 숫자 변환
        try:
            price = int(price)
        except ValueError:
            messagebox.showwarning("입력 오류", "가격은 숫자만 입력해주세요.")
            return

        try:
            print("✅ 게시글 등록 시작")
            conn = get_connection()
            with conn.cursor() as cursor:
                # 1. 사용자 조회
                cursor.execute("SELECT user_id FROM User WHERE email = %s", (user_email,))
                user_result = cursor.fetchone()
                if not user_result:
                    raise Exception("❌ 사용자가 존재하지 않습니다.")
                user_id = user_result[0]
                print("🧑 사용자 ID:", user_id)

                # 2. Item INSERT
                cursor.execute("""
                    INSERT INTO Item (product_type, title, description, size)
                    VALUES (%s, %s, %s, %s)
                """, (product_type, title, description, size))
                item_id = cursor.lastrowid
                print("📦 Item ID:", item_id)

                # 3. Post INSERT
                cursor.execute("""
                    INSERT INTO Post (user_id, item_id, price, location)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, item_id, price, location))
                post_id = cursor.lastrowid
                print("📝 Post ID:", post_id)

                # 4. Image INSERT (옵션)
                if image_url:
                    cursor.execute("""
                        INSERT INTO Image (item_item_id, image_url)
                        VALUES (%s, %s)
                    """, (item_id, image_url))
                    print("🖼 이미지 URL 등록됨")

                # 최종 반영
                conn.commit()
                messagebox.showinfo("성공", "게시글이 등록되었습니다!")
                win.destroy()

        except Exception as e:
            print("❌ 예외 발생:", repr(e))
            messagebox.showerror("DB 오류", str(e))

        finally:
            if conn:
                conn.close()

    # --- 버튼 생성 ---
    tk.Button(win, text="게시글 등록", command=submit_post).pack(pady=20)
import tkinter as tk
from tkinter import messagebox, ttk
from db_connect import get_connection  # DB 연결 함수

def open_write_post(user_email):
    win = tk.Toplevel()
    win.title("📝 게시글 작성하기")
    win.geometry("500x600")

    # --- UI 입력 필드 ---
    tk.Label(win, text="제목").pack()
    title_entry = tk.Entry(win, width=50)
    title_entry.pack()

    tk.Label(win, text="설명").pack()
    desc_text = tk.Text(win, height=4, width=50)
    desc_text.pack()

    tk.Label(win, text="가격").pack()
    price_entry = tk.Entry(win)
    price_entry.pack()

    tk.Label(win, text="위치").pack()
    location_entry = tk.Entry(win)
    location_entry.pack()

    tk.Label(win, text="상품 유형").pack()
    product_type_combo = ttk.Combobox(win, values=["하키복", "농구조끼", "티셔츠", "야구점퍼"])
    product_type_combo.pack()

    tk.Label(win, text="사이즈").pack()
    size_combo = ttk.Combobox(win, values=["SMALL", "MEDIUM", "LARGE"])  # DB enum 값과 일치
    size_combo.pack()

    tk.Label(win, text="이미지 URL").pack()
    image_entry = tk.Entry(win, width=50)
    image_entry.pack()

    # --- 게시글 등록 함수 ---
    def submit_post():
        title = title_entry.get()
        description = desc_text.get("1.0", "end").strip()
        price = price_entry.get()
        location = location_entry.get()
        product_type = product_type_combo.get()
        size = size_combo.get()
        image_url = image_entry.get()

        # 필수 항목 체크
        if not all([title, description, price, location, product_type, size]):
            messagebox.showwarning("입력 오류", "모든 항목을 입력해주세요.")
            return

        # 가격 숫자 확인
        try:
            price = int(price)
        except ValueError:
            messagebox.showwarning("입력 오류", "가격은 숫자만 입력해주세요.")
            return

        try:
            print("✅ 게시글 등록 시작")
            conn = get_connection()
            with conn.cursor() as cursor:
                # 1. 사용자 조회
                cursor.execute("SELECT user_id FROM User WHERE email = %s", (user_email,))
                user_result = cursor.fetchone()
                if not user_result:
                    raise Exception("❌ 사용자가 존재하지 않습니다.")
                user_id = user_result["user_id"]
                print("🧑 사용자 ID:", user_id)

                # 2. Item INSERT
                cursor.execute("""
                    INSERT INTO Item (product_type, title, description, size)
                    VALUES (%s, %s, %s, %s)
                """, (product_type, title, description, size))
                item_id = cursor.lastrowid
                print("📦 Item ID:", item_id)

                # 3. Post INSERT
                cursor.execute("""
                    INSERT INTO Post (user_id, item_id, price, location)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, item_id, price, location))
                post_id = cursor.lastrowid
                print("📝 Post ID:", post_id)

                # 4. Image INSERT (옵션)
                if image_url:
                    cursor.execute("""
                        INSERT INTO Image (item_item_id, image_url)
                        VALUES (%s, %s)
                    """, (item_id, image_url))
                    print("🖼 이미지 등록됨")

                conn.commit()
                messagebox.showinfo("성공", "게시글이 등록되었습니다!")
                win.destroy()

        except Exception as e:
            print("❌ 예외 발생:", repr(e))
            messagebox.showerror("DB 오류", str(e))

        finally:
            if conn:
                conn.close()

    # --- 등록 버튼 ---
    tk.Button(win, text="게시글 등록", command=submit_post).pack(pady=20)
import tkinter as tk
from tkinter import messagebox, ttk
from db_connect import get_connection  # DB 연결 함수

def open_write_post(user_id):
    win = tk.Toplevel()
    win.title("📝 게시글 작성하기")
    win.geometry("500x600")

    # --- UI 입력 필드 ---
    tk.Label(win, text="제목").pack()
    title_entry = tk.Entry(win, width=50)
    title_entry.pack()

    tk.Label(win, text="설명").pack()
    desc_text = tk.Text(win, height=4, width=50)
    desc_text.pack()

    tk.Label(win, text="가격").pack()
    price_entry = tk.Entry(win)
    price_entry.pack()

    tk.Label(win, text="위치").pack()
    location_entry = tk.Entry(win)
    location_entry.pack()

    tk.Label(win, text="상품 유형").pack()
    product_type_combo = ttk.Combobox(win, values=["하키복", "농구조끼", "티셔츠", "야구점퍼"])
    product_type_combo.pack()

    tk.Label(win, text="사이즈").pack()
    size_combo = ttk.Combobox(win, values=["SMALL", "MEDIUM", "LARGE"])  # DB enum 값과 일치
    size_combo.pack()

    tk.Label(win, text="이미지 URL").pack()
    image_entry = tk.Entry(win, width=50)
    image_entry.pack()

    # --- 게시글 등록 함수 ---
    def submit_post():
        title = title_entry.get()
        description = desc_text.get("1.0", "end").strip()
        price = price_entry.get()
        location = location_entry.get()
        product_type = product_type_combo.get()
        size = size_combo.get()
        image_url = image_entry.get()

        # 필수 항목 체크
        if not all([title, description, price, location, product_type, size]):
            messagebox.showwarning("입력 오류", "모든 항목을 입력해주세요.")
            return

        # 가격 숫자 확인
        try:
            price = int(price)
        except ValueError:
            messagebox.showwarning("입력 오류", "가격은 숫자만 입력해주세요.")
            return

        try:
            print("✅ 게시글 등록 시작 (user_id =", user_id, ")")
            conn = get_connection()
            with conn.cursor() as cursor:
                # 1. Item INSERT
                cursor.execute("""
                    INSERT INTO Item (product_type, title, description, size)
                    VALUES (%s, %s, %s, %s)
                """, (product_type, title, description, size))
                item_id = cursor.lastrowid
                print("📦 Item ID:", item_id)

                # 2. Post INSERT
                cursor.execute("""
                    INSERT INTO Post (user_id, item_id, price, location)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, item_id, price, location))
                post_id = cursor.lastrowid
                print("📝 Post ID:", post_id)

                # 3. Image INSERT (옵션)
                if image_url:
                    cursor.execute("""
                        INSERT INTO Image (item_item_id, image_url)
                        VALUES (%s, %s)
                    """, (item_id, image_url))
                    print("🖼 이미지 등록됨")

                conn.commit()
                messagebox.showinfo("성공", "게시글이 등록되었습니다!")
                win.destroy()

        except Exception as e:
            print("❌ 예외 발생:", repr(e))
            messagebox.showerror("DB 오류", str(e))

        finally:
            if conn:
                conn.close()

    # --- 등록 버튼 ---
    tk.Button(win, text="게시글 등록", command=submit_post).pack(pady=20)
