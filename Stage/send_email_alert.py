import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = ""
PASSWORD = ""
TO_EMAIL = ""  # tu peux mettre une autre adresse si tu veux

SMTP_SERVER = "smtp.cmi.univ-mrs.fr"
SMTP_PORT = 587  # généralement 587 pour TLS

def send_email(reason):
    subject = "🚨 ALERT: Database Monitoring"
    body = f"Alert triggered:\n\n{reason}\n\nPlease investigate the system."

    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # démarre TLS
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
            print(f"[INFO] Alert email sent: {reason}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

if __name__ == "__main__":
    send_email("Test alert from university SMTP server")
