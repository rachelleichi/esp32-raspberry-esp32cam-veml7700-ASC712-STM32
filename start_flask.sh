#!/bin/bash

echo "📁 Passage dans le dossier Stage..."
cd /home/rachel/esp32-raspberry-esp32cam-veml7700-ASC712-STM32/Stage || exit 1

echo "🐍 Activation de l'environnement virtuel..."
source ../venv/bin/activate

echo "🚀 Lancement des serveurs Flask..."

# Serveur YOLOv8
export FLASK_APP=yolov8.py
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 --port=5010 > ../yolov8.log 2>&1 &

# Serveur Dashboard
export FLASK_APP=dashboard.py
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 --port=5011 > ../dashboard.log 2>&1 &

echo "✅ Serveurs Flask démarrés avec succès !"