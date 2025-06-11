#!/usr/bin/env python3

import time
import serial
import mysql.connector

# Configuration MariaDB
db_config = {
    'host': 'localhost',
    'user': 'rachel',
    'password': 'Stage.2025',
    'database': 'Stage'
}

# Port série Bluetooth
serial_port = '/dev/rfcomm0'
baud_rate = 9600  

def insert_data(luminosite, presence):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insérer dans la table luminosite
        cursor.execute(
            "INSERT INTO luminosite (taux_luminosite) VALUES (%s)",
            (luminosite,)
        )

        # Insérer dans la table presence
        cursor.execute(
            "INSERT INTO presence (presence_detected) VALUES (%s)",
            (presence,)
        )

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[✔] Données insérées : Luminosité = {luminosite}, Présence = {presence}")

    except mysql.connector.Error as err:
        print(f"[❌] Erreur base de données : {err}")

def main():
    print(f"🔌 Connexion au port {serial_port}...")
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=2)
        print("✅ Port série ouvert. En attente de données...\n")

        while True:
            try:
                line = ser.readline().decode().strip()
                if not line:
                    continue

                print(f"📨 Reçu : {line}")
                if '-' in line:
                    parts = line.split('-')
                    if len(parts) == 2:
                        luminosite = float(parts[0])
                        presence = int(parts[1])
                        insert_data(luminosite, presence)
                    else:
                        print(f"[⚠️] Format invalide : {line}")
                else:
                    print(f"[⚠️] Pas de séparateur '-' trouvé : {line}")

            except Exception as e:
                print(f"[❌] Erreur de lecture ou de parsing : {e}")
                time.sleep(1)

    except serial.SerialException as e:
        print(f"[❌] Impossible d'ouvrir le port série : {e}")

if __name__ == "__main__":
    main()