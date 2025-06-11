import mysql.connector

# DB connection
conn = mysql.connector.connect(
    host="localhost",
    user="rachel",
    password="Stage.2025",
    database="Stage"
)
cursor = conn.cursor()

try:
    for table in ['presence', 'luminosite', 'intensite']:
        cursor.execute(f"DELETE FROM {table}")
        print(f"[INFO] Deleted all rows from {table}")

    conn.commit()
except mysql.connector.Error as err:
    print(f"[ERROR] {err}")
finally:
    cursor.close()
    conn.close()
