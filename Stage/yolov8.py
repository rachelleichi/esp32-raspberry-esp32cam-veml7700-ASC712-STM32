from flask import Flask, request
from datetime import datetime
import os
import mysql.connector
from ultralytics import YOLO

app = Flask(__name__)

# Constantes
UPLOAD_FOLDER = 'uploads_yolov8'
STATUS_FILE = os.path.join(UPLOAD_FOLDER, 'status.txt')

db_config = {
    'user': 'rachel',
    'password': 'Stage.2025',
    'host': 'localhost',
    'database': 'Stage'
}

# Création du dossier d’upload si nécessaire
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Variable globale pour stocker le chemin de la dernière image
last_image_path = None

# Chargement du modèle YOLOv8
model = YOLO("models/yolov8n.pt")

# Fonction utilitaire pour obtenir une connexion DB
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return "<h2>ESP32 Image Upload Server with YOLOv8 Presence Detection</h2>", 200

# Détection de présence via YOLOv8
def detect_presence(image_path):
    results = model(image_path)
    for result in results:
        if any(int(cls) == 0 for cls in result.boxes.cls):
            print("[INFO] Person detected by YOLOv8")
            return True
    print("[INFO] No person detected by YOLOv8")
    return False

# Enregistrement de la détection dans MariaDB
def save_presence_to_db(presence_flag):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO presence (presence_detected) VALUES (%s)", (presence_flag,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"[ERROR] MariaDB error: {err}")
    finally:
        cursor.close()
        conn.close()

@app.route('/uploads', methods=['POST'])
def upload_file():
    global last_image_path

    file = request.files.get('imageFile')
    if not file or file.filename == '':
        return "No file provided", 400

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"capture_YOLOv8_{timestamp}_presence_0.jpg"
        temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_filepath)
        print(f"[INFO] New image saved: {temp_filename}")

        if last_image_path and os.path.exists(last_image_path):
            os.remove(last_image_path)
            print(f"[INFO] Removed previous image: {last_image_path}")

        presence_detected = detect_presence(temp_filepath)
        presence_flag = 1 if presence_detected else 0

        final_filename = f"capture_YOLOv8_{timestamp}_presence_{presence_flag}.jpg"
        final_filepath = os.path.join(UPLOAD_FOLDER, final_filename)
        os.rename(temp_filepath, final_filepath)
        last_image_path = final_filepath
        print(f"[INFO] Image renamed to {final_filename}")

        with open(STATUS_FILE, 'w') as f:
            f.write(str(presence_flag))

        save_presence_to_db(presence_flag)

        return "Presence Detected" if presence_detected else "No Presence Detected", 200

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Error saving image", 500

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    try:
        lux = float(data.get("lux", 0))
        current = float(data.get("current", 0))
        power = float(data.get("power", 0))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO luminosite (taux_luminosite) VALUES (%s)", (lux,))
        cursor.execute("INSERT INTO intensite (courant, puissance) VALUES (%s, %s)", (current, power))

        conn.commit()
        return {"status": "success", "message": "Data inserted in DB"}, 200

    except Exception as e:
        print("Erreur :", e)
        return {"status": "error", "message": str(e)}, 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
