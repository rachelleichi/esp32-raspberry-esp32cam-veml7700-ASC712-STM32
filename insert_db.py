import mysql.connector
from datetime import datetime, timedelta
import random

# DB connection info
config = {
    'user': 'rachel',
    'password': 'Stage.2025',
    'host': 'localhost',  # Adjust if your DB host is different
    'database': 'Stage',
}

def generate_timestamps(start, count, delta_minutes=10):
    return [start + timedelta(minutes=i * delta_minutes) for i in range(count)]

def insert_luminosite(cursor, timestamps):
    sql = "INSERT INTO luminosite (timestamp, taux_luminosite) VALUES (%s, %s)"
    for ts in timestamps:
        taux = round(random.uniform(0, 100), 2)  # 0-100% luminosity
        cursor.execute(sql, (ts, taux))

def insert_presence(cursor, timestamps):
    sql = "INSERT INTO presence (timestamp, presence_detected) VALUES (%s, %s)"
    for ts in timestamps:
        presence = random.choice([0, 1])
        cursor.execute(sql, (ts, presence))

def insert_intensite(cursor, timestamps):
    sql = "INSERT INTO intensite (timestamp, courant, puissance) VALUES (%s, %s, %s)"
    for ts in timestamps:
        courant = round(random.uniform(0, 15), 2)   # Amperes
        puissance = round(random.uniform(0, 500), 2) # Watts
        cursor.execute(sql, (ts, courant, puissance))

def main():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        count = 50
        start_time = datetime.now() - timedelta(days=1)
        timestamps = generate_timestamps(start_time, count)

        insert_luminosite(cursor, timestamps)
        insert_presence(cursor, timestamps)
        insert_intensite(cursor, timestamps)

        cnx.commit()
        print("✅ Inserted 50 rows into each table successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
