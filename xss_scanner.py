import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import html
import threading
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def send_telegram_message(message):
    TELEGRAM_BOT_TOKEN = '7543882357:AAH07v_WNLvxuTTrGFHuoOuMVYtA3iS2AzY'
    TELEGRAM_CHAT_ID = '1780641008'
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return None

def load_payloads_from_file():
    payloads = []
    file_path = "xss-payload-list.txt"  # اسم الملف

    # التحقق من وجود الملف
    if not os.path.isfile(file_path):
        messagebox.showerror("Error", f"The file '{file_path}' is not found!")
        return []

    try:
        # فتح الملف النصي وقراءة البايلودات
        with open(file_path, "r", encoding="utf-8") as file:
            payloads = file.readlines()

        # تنظيف البايلودات (إزالة الفراغات والتباعد الزائد)
        payloads = [payload.strip() for payload in payloads]

        if not payloads:
            messagebox.showerror("Error", "No payloads found in the file!")

        return payloads
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return []


# ================= واجهة البرنامج ==============
root = tk.Tk()
root.title("XSS Testing Tool")
root.geometry("1300x800")
root.configure(bg="#2c3e50")

top_frame = tk.Frame(root, bg="#34495e", padx=10, pady=10)
top_frame.pack(fill="x", padx=10, pady=10)

tk.Label(top_frame, text="Target URL", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#34495e").grid(row=0, column=0,
                                                                                                    padx=5)
ip_entry = ttk.Entry(top_frame, font=("Arial", 12), width=40)
ip_entry.grid(row=0, column=1, padx=5)

tk.Label(top_frame, text="Tester Name", font=("Arial", 12, "bold"), fg="#ecf0f1", bg="#34495e").grid(row=0, column=2,
                                                                                                     padx=5)
tester_entry = ttk.Entry(top_frame, font=("Arial", 12), width=20)
tester_entry.grid(row=0, column=3, padx=5)

save_button = ttk.Button(top_frame, text="Save Report")
save_button.grid(row=1, column=0, pady=10)

scan_button = ttk.Button(top_frame, text="Start Scan")
scan_button.grid(row=1, column=1, pady=10)

stop_button = ttk.Button(top_frame, text="Stop Scan")
stop_button.grid(row=1, column=2, pady=10)

status_label = tk.Label(top_frame, text="Idle", font=("Arial", 12), fg="#2ecc71", bg="#34495e")
status_label.grid(row=2, column=0, columnspan=4, pady=10)

table_frame = tk.Frame(root, bg="#2c3e50", padx=10, pady=10)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

# إضافة عمود جديد لعرض عنوان الرابط
columns = ("Payload", "Status", "Details", "URL")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
for col in columns:
    table.heading(col, text=col, anchor="center")
    table.column(col, width=300, anchor="center")

style = ttk.Style()
style.configure("Treeview", font=("Arial", 12))
style.configure("Treeview.Heading", font=("Arial", 14, "bold"), foreground="black")

scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
table.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
table.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

style.configure("TButton", font=("Arial", 12, "bold"), padding=10, foreground="black", background="#34495e")

# ================= دالة اختبار XSS =================
is_scanning = False  # متغير لتحديد ما إذا كان الفحص جاريًا
start_time = None  # لحفظ وقت بدء الفحص
end_time = None  # لحفظ وقت انتهاء الفحص
chat=""

def test_xss():
    global is_scanning, start_time, end_time
    target_url = ip_entry.get()
    tester_name = tester_entry.get()
    payloads = load_payloads_from_file()
    if not target_url or not tester_name or not payloads:
        messagebox.showerror("Error", "Please enter the target URL, tester name, and ensure payloads are loaded.")
        return
    lable_payload = ""
    start_time = time.time()  # تسجيل وقت بدء الفحص
    status_label.config(text=fr"Scanning...{lable_payload}", fg="orange")
    table.delete(*table.get_children())  # Clear the table
    successful_payloads = []  # قائمة لحفظ جميع البايلودات الناجحة
# http://www.sudo.co.il/xss/level0.php?email=
    for payload in payloads:
        if not is_scanning:
            break
        try:
            full_url = target_url + payload
            response = requests.get(full_url, timeout=5)
            lable_payload = payload+""
            # استخراج النص من استجابة الموقع وتحويله إلى شكل قابل للمقارنة
            soup = BeautifulSoup(response.text, "html.parser")
            response_text = soup.get_text()
            unescaped_response = html.unescape(response_text)
            # فحص إذا كان البايلود موجودًا في أي شكل من أشكال النصوص
            if any(p in response.text for p in [payload, html.escape(payload), html.unescape(payload)]) or \
                    any(p in response_text for p in [payload, html.escape(payload), html.unescape(payload)]) or \
                    any(p in unescaped_response for p in [payload, html.escape(payload), html.unescape(payload)]):
                result_status = "XSS Detected"
                details = f"Payload: {payload}"
                send_telegram_message(f"Threats Detected...\nRisk : High\nTarget : {target_url}\nType : XSS.\n "
                                          f"Payloads : {payload}")
                # إضافة عنوان الرابط الذي تم فيه العثور على الثغرة
                table.insert("", "end", values=(payload, result_status, details, full_url))
                successful_payloads.append(full_url)  # حفظ الرابط الناجح
        except requests.exceptions.RequestException as e:
            continue  # تجاهل الأخطاء

    end_time = time.time()  # تسجيل وقت انتهاء الفحص

    # # إذا تم العثور على XSS
    # if successful_payloads:
    #     status_label.config(text="XSS Found", fg="red")
    # else:
    #     status_label.config(text="No XSS Detected", fg="#2ecc71")


# ================= دالة تشغيل الفحص في خيط =================
def start_scan():
    global is_scanning
    is_scanning = True
    scan_thread = threading.Thread(target=test_xss)
    scan_thread.start()


# ================= دالة إيقاف الفحص =================
def stop_scan():
    global is_scanning
    is_scanning = False

    status_label.config(text="Scan Stopped", fg="red")


# ================= دالة حفظ التقرير بصيغة PDF =================
def save_report():
    try:
        # استرجاع جميع البيانات من الجدول
        rows = table.get_children()
        if not rows:
            messagebox.showerror("Error", "No data to save!")
            return

        # تحديد اسم الملف
        file_name = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_name:
            return  # إذا تم إلغاء الحفظ

        # إنشاء مستند PDF
        pdf = canvas.Canvas(file_name, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 16)

        # كتابة عنوان التقرير
        pdf.drawString(100, 750, "XSS Test Report")
        pdf.setFont("Helvetica", 12)
        # pdf.drawString(100, 730, f"Test Type: XSS Scan")
        pdf.drawString(100, 710, f"Tester: {tester_entry.get()}")
        pdf.drawString(100, 690, f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
        pdf.drawString(100, 670, f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        pdf.drawString(100, 650, f"Successful Payloads: {len(table.get_children())}")
        #pdf.drawString(100,800,"How to solv XSS :",nr.ask_openrouter("How to solv xss problem ?",api_key))

        y_position = 620

        # كتابة البيانات في الملف
        for row in rows:
            payload, status, details, url = table.item(row)["values"]
            y_position -= 20
            pdf.drawString(100, y_position, f"Payload: {payload}")
            y_position -= 20
            pdf.drawString(100, y_position, f"Status: {status}")
            y_position -= 20
            pdf.drawString(100, y_position, f"Details: {details}")
            y_position -= 20
            pdf.drawString(100, y_position, f"URL: {url}")
            y_position -= 30  # إضافة مسافة بين كل نتيجة

        # حفظ الملف
        pdf.save()

        messagebox.showinfo("Success", "Report saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the report: {e}")


# ================= ربط الأزرار بالوظائف =================
scan_button.config(command=start_scan)
stop_button.config(command=stop_scan)
save_button.config(command=save_report)

root.mainloop()
