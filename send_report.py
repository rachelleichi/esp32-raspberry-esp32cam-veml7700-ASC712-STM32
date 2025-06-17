import smtplib
from email.message import EmailMessage
import os
from datetime import datetime

# SMTP and email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # See below
RECEIVER_EMAIL = "your_email@gmail.com"  # or someone else

# File to send
today = datetime.now().strftime('%Y%m%d')
file_to_send = f"weekly_report_{today}.xlsx"

if not os.path.exists(file_to_send):
    print(f"[ERROR] File not found: {file_to_send}")
    exit(1)

# Create email message
msg = EmailMessage()
msg["Subject"] = f"Weekly Report - {today}"
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg.set_content("Attached is this week's Excel report.")

# Attach Excel file
with open(file_to_send, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_to_send
    )

# Send email
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
        print("[INFO] Email sent successfully!")
except Exception as e:
    print(f"[ERROR] Failed to send email: {e}")
