import mysql.connector
from datetime import datetime, timedelta

# DB connection
conn = mysql.connector.connect(
    host="localhost",
    user="rachel",
    password="Stage.2025",
    database="Stage"
)
cursor = conn.cursor()

# Tables to process
tables = ['presence', 'luminosite', 'intensite']

print("Quel mode souhaitez-vous utiliser pour la suppression ?")
print("1. Supprimer un jour spécifique (day)")
print("2. Supprimer les données de plus de 7 jours (week)")
print("3. Supprimer les N dernières entrées (last_n)")
print("4. Supprimer entre deux timestamps (range)")
choice = input("Entrez 1, 2, 3 ou 4 : ").strip()

try:
    if choice == '1':
        target_day = input("Entrez la date au format AAAA-MM-JJ (ex: 2025-06-03) : ").strip()
        try:
            datetime.strptime(target_day, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Format de date invalide.")
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE DATE(timestamp) = %s", (target_day,))
            print(f"[INFO] Lignes supprimées de {table} pour la date {target_day}")

    elif choice == '2':
        one_week_ago = datetime.now() - timedelta(days=7)
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE timestamp < %s", (one_week_ago,))
            print(f"[INFO] Lignes supprimées de {table} datant de plus de 7 jours")

    elif choice == '3':
        N = input("Combien de dernières entrées souhaitez-vous supprimer ? : ").strip()
        if not N.isdigit() or int(N) <= 0:
            raise ValueError("Veuillez entrer un nombre entier positif.")
        N = int(N)
        for table in tables:
            cursor.execute(f"""
                DELETE FROM {table}
                WHERE id IN (
                    SELECT id FROM (
                        SELECT id FROM {table} ORDER BY timestamp DESC LIMIT %s
                    ) AS sub
                )
            """, (N,))
            print(f"[INFO] Dernières {N} entrées supprimées de {table}")

    elif choice == '4':
        print("Entrez l'intervalle de temps complet pour la suppression.")
        start_ts = input("🕓 Début (format: AAAA-MM-JJ HH:MM:SS) : ").strip()
        end_ts = input("🕓 Fin   (format: AAAA-MM-JJ HH:MM:SS) : ").strip()

        try:
            dt_start = datetime.strptime(start_ts, "%Y-%m-%d %H:%M:%S")
            dt_end = datetime.strptime(end_ts, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Les dates doivent être au format complet : AAAA-MM-JJ HH:MM:SS")

        if dt_end <= dt_start:
            raise ValueError("La date de fin doit être postérieure à la date de début.")

        for table in tables:
            cursor.execute(f"""
                DELETE FROM {table}
                WHERE timestamp BETWEEN %s AND %s
            """, (dt_start, dt_end))
            print(f"[INFO] Données supprimées de {table} entre {start_ts} et {end_ts}")

    else:
        print("[ERREUR] Choix invalide. Veuillez entrer 1, 2, 3 ou 4.")

    conn.commit()

except mysql.connector.Error as err:
    print(f"[ERREUR MySQL] {err}")
except ValueError as ve:
    print(f"[ERREUR] {ve}")
finally:
    cursor.close()
    conn.close()
