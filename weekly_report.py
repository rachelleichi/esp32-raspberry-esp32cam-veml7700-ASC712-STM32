import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import os

# Connexion à la base de données
conn = mysql.connector.connect(
    host="localhost",
    user="rachel",
    password="Stage.2025",
    database="Stage"
)

one_week_ago = datetime.now() - timedelta(days=7)

tables = {
    "presence": "SELECT timestamp, presence_detected FROM presence WHERE timestamp >= %s",
    "luminosite": "SELECT timestamp, taux_luminosite FROM luminosite WHERE timestamp >= %s",
    "intensite": "SELECT timestamp, courant, puissance FROM intensite WHERE timestamp >= %s"
}

dataframes = {}

for name, query in tables.items():
    cursor = conn.cursor()
    cursor.execute(query, (one_week_ago,))
    rows = cursor.fetchall()
    columns = cursor.column_names
    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        print(f"[INFO] No data for table '{name}' this week.")
        continue

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    dataframes[name] = df

    # 📊 Génération du graphique
    plt.figure(figsize=(10, 4))
    x = df['timestamp']

    if name == "intensite":
        for col in df.columns[1:]:
            plt.plot(x, df[col], label=col, marker='o', markersize=3, linestyle='-')
    else:
        plt.bar(x, df[df.columns[1]], width=0.03, label=df.columns[1], alpha=0.7)

    plt.title(f"{name.capitalize()} - 7 derniers jours")
    plt.xlabel("Horodatage")
    plt.ylabel("Valeur")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_path = f"{name}_week_plot.png"
    plt.savefig(image_path)
    plt.close()
    print(f"[INFO] Plot saved: {image_path}")

    # 💾 Export CSV individuel
    csv_path = f"{name}_report_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"[INFO] CSV export saved: {csv_path}")

    cursor.close()

conn.close()

if not dataframes:
    print("[WARNING] No data found — no CSV generated.")
