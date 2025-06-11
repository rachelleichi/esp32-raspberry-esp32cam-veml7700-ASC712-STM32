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

# Tables à traiter
tables = ['presence', 'luminosite', 'intensite']

print("Quel mode souhaitez-vous utiliser pour la suppression ?")
print("1. Supprimer un jour spécifique (day)")
print("2. Supprimer les données de plus de 7 jours (week)")
print("3. Supprimer les N dernières entrées (last_n)")
choice = input("Entrez 1, 2 ou 3 : ").strip()

try:
    if choice == '1':
        mode = 'day'
        target_day = input("Entrez la date au format AAAA-MM-JJ (ex: 2025-06-03) : ").strip()
        try:
            datetime.strptime(target_day, "%Y-%m-%d")  # validation de la date
        except ValueError:
            raise ValueError("Format de date invalide.")
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE DATE(timestamp) = %s", (target_day,))
            print(f"[INFO] Lignes supprimées de {table} pour la date {target_day}")

    elif choice == '2':
        mode = 'week'
        one_week_ago = datetime.now() - timedelta(days=7)
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE timestamp < %s", (one_week_ago,))
            print(f"[INFO] Lignes supprimées de {table} datant de plus de 7 jours")

    elif choice == '3':
        mode = 'last_n'
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

    else:
        print("[ERREUR] Choix invalide. Veuillez entrer 1, 2 ou 3.")

    conn.commit()

except mysql.connector.Error as err:
    print(f"[ERREUR MySQL] {err}")
except ValueError as ve:
    print(f"[ERREUR] {ve}")
finally:
    cursor.close()
    conn.close()