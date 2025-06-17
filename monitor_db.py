import mysql.connector
from datetime import datetime, timedelta
import subprocess

DB_CONFIG = {
    'user': 'rachel',
    'password': 'Stage.2025',
    'host': 'localhost',
    'database': 'Stage'
}

LOG_FILE = "alert_logs.txt"

# 📓 Fonction pour écrire les logs d'alerte dans un fichier
def log_alert(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# 🔔 Send alert using external script + log alert locally
def send_alert(reason):
    print(f"[ALERT] Reason: {reason}")
    log_alert(reason)
    try:
        subprocess.run(["python3", "send_email_alert.py", reason])
    except Exception as e:
        # En cas d'erreur d'envoi, on logue aussi
        log_alert(f"Failed to send email alert: {e}")

# ✅ Check logic for a given table and column
def check_table(cursor, table, column):
    try:
        # Fetch last 5 entries
        cursor.execute(f"SELECT {column}, timestamp FROM {table} ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()

        if len(rows) == 5:
            values = [row[0] for row in rows]
            if all(v == values[0] for v in values):
                send_alert(f"Same value in '{table}.{column}' repeated 5 times.")

        # Check if no recent data
        if rows:
            last_time = rows[0][1]
            if datetime.now() - last_time > timedelta(minutes=30):
                send_alert(f"No new data in '{table}' table for the last 30 minutes.")

    except mysql.connector.Error as err:
        error_msg = f"[ERROR] While checking table {table}: {err}"
        print(error_msg)
        send_alert(f"Database error in table '{table}': {err}")

# 📦 Main check routine
def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        check_table(cursor, "presence", "presence_detected")
        check_table(cursor, "luminosite", "taux_luminosite")
        check_table(cursor, "intensite", "courant")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[DB ERROR] {err}")
        send_alert("Database connection failed.")

if __name__ == "__main__":
    main()
