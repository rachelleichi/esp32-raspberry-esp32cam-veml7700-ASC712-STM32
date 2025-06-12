#!/bin/bash

set -e

# ------------------------------
# Vérification root
# ------------------------------
if [ "$(id -u)" -ne 0 ]; then
  echo "❌ Ce script doit être exécuté en tant que root (sudo)"
  exit 1
fi

echo "🛠️  Mise à jour du système..."
apt update && apt upgrade -y

# ------------------------------
# MariaDB
# ------------------------------
echo "📦 Installation de MariaDB..."
apt install -y mariadb-server

echo "🔒 Sécurisation MariaDB..."
mysql_secure_installation <<EOF

y
n
y
y
y
EOF

# DB setup
DB_NAME="Stage"
DB_USER="rachel"
DB_PASS="Stage.2025"
DB_HOST="%"

echo "🔐 Création base + utilisateur MariaDB..."
mysql -e "
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'${DB_HOST}';
FLUSH PRIVILEGES;

USE ${DB_NAME};

CREATE TABLE IF NOT EXISTS presence (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  presence_detected TINYINT(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS luminosite (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  taux_luminosite FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS intensite (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  courant FLOAT NOT NULL,
  puissance FLOAT NOT NULL
);
"

# ------------------------------
# Python & Environnement virtuel
# ------------------------------
echo "🐍 Installation de Python et dépendances..."
apt install -y python3-pip python3-venv xdg-utils

echo "📦 Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
else
  echo "ℹ️ Le dossier venv existe déjà, saut de création."
fi
source venv/bin/activate

echo "📦 Installation des paquets Python depuis paquets.txt..."
pip install --upgrade pip
pip install --prefer-binary -r paquets.txt

# ------------------------------
# Téléchargement du modèle YOLO
# ------------------------------
echo "📥 Téléchargement du modèle YOLOv8..."
mkdir -p Stage/models
YOLO_MODEL="Stage/models/yolov8n.pt"
if [ ! -s "$YOLO_MODEL" ]; then
  wget -O "$YOLO_MODEL" https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
else
  echo "ℹ️ Le modèle YOLOv8 existe déjà et n'est pas vide, saut du téléchargement."
fi

# ------------------------------
# Création des fichiers statiques (Bootstrap / Chart.js pour usage offline)
# ------------------------------
echo "🌐 Téléchargement de Bootstrap & Chart.js (mode hors-ligne)..."
mkdir -p Stage/static/libs

BOOTSTRAP_CSS="Stage/static/libs/bootstrap.min.css"
CHART_JS="Stage/static/libs/chart.min.js"

if [ ! -s "$BOOTSTRAP_CSS" ]; then
  wget -q -O "$BOOTSTRAP_CSS" https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
else
  echo "ℹ️ Bootstrap CSS déjà présent."
fi

if [ ! -s "$CHART_JS" ]; then
  wget -q -O "$CHART_JS" https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js
else
  echo "ℹ️ Chart.js déjà présent."
fi

echo "✅ Bibliothèques frontend prêtes dans Stage/static/libs/"

# ------------------------------
# Lancement automatique des serveurs Flask
# ------------------------------
echo "🚀 Lancement des serveurs Flask..."

# Serveur YOLOv8
export FLASK_APP=Stage/yolov8.py
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 --port=5010 > yolov8.log 2>&1 &

# Serveur Dashboard
export FLASK_APP=Stage/dashboard.py
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 --port=5011 > dashboard.log 2>&1 &

echo "✅ Tout est prêt !"
echo " - Serveur YOLOv8 est lancé sur le port 5010."
echo " - Serveur Dashboard est lancé sur le port 5011."
echo "🔁 Redémarre le Pi si nécessaire avec : sudo reboot"
