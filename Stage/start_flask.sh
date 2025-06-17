#!/bin/bash

# === CONFIGURATION ===
Y8_LOG="../yolov8.log"
DB_LOG="../dashboard.log"
MAX_SIZE=$((1024 * 1024)) # 1MB en octets

# === FONCTION : Nettoyage si trop gros ===
cleanup_log() {
  local log_file="$1"
  
  [ ! -f "$log_file" ] && touch "$log_file"

  size=$(stat -c%s "$log_file")

  if [ "$size" -gt "$MAX_SIZE" ]; then
    echo "🧹 Log trop gros (>1MB), nettoyage de $log_file"
    : > "$log_file"
  fi
}

echo "📁 Passage dans le dossier Stage..."
cd /home/rachel/esp32-raspberry-esp32cam-veml7700-ASC712-STM32/Stage || exit 1

echo "🐍 Activation de l'environnement virtuel..."
source ../venv/bin/activate

# Nettoyage conditionnel des logs
cleanup_log "$Y8_LOG"
cleanup_log "$DB_LOG"

echo "🚀 Lancement des serveurs Flask..."

# Serveur YOLOv8
export FLASK_APP=yolov8.py
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 --port=5010 >> "$Y8_LOG" 2>&1 &

# Serveur Dashboard
export FLASK_APP=dashboard.py
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 --port=5011 >> "$DB_LOG" 2>&1 &

echo "✅ Serveurs Flask démarrés avec succès !"
