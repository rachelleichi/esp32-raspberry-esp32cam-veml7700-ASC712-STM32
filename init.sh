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
# Bluetooth
# ------------------------------
# echo "📶 Installation Bluetooth..."
# apt install -y bluez pi-bluetooth

# echo "🔗 Configuration de liaison Bluetooth série..."
# cat > /etc/systemd/system/bluetooth-serial.service <<EOF
# [Unit]
# Description=Connexion Bluetooth série STM32
# After=bluetooth.target

# [Service]
# ExecStart=/usr/bin/rfcomm bind /dev/rfcomm0 0209135d42f2
# ExecStop=/usr/bin/rfcomm release /dev/rfcomm0
# Restart=on-failure

# [Install]
# WantedBy=multi-user.target
# EOF

# systemctl daemon-reexec
# systemctl daemon-reload
# systemctl enable bluetooth-serial.service

# echo "⚠️ Adresse MAC par défaut utilisée (0209135d42f2). Modifie-la si besoin !"

# ------------------------------
# Python & Environnement virtuel
# ------------------------------
echo "🐍 Installation de Python et dépendances..."
apt install -y python3-pip python3-venv xdg-utils

echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installation des paquets Python depuis paquets.txt..."
pip install --upgrade pip
pip install --prefer-binary -r paquets.txt


# echo "📦 Installation de tkinter..."
# apt install -y python3-tk

# ------------------------------
# Téléchargement du modèle YOLO
# ------------------------------
echo "📥 Téléchargement du modèle YOLOv8..."
mkdir -p Stage/models
wget -O Stage/models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt


# ------------------------------
# Création des fichiers statiques (Bootstrap / Chart.js pour usage offline)
# ------------------------------
echo "🌐 Téléchargement de Bootstrap & Chart.js (mode hors-ligne)..."
mkdir -p Stage/static/libs

wget -q -O Stage/static/libs/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
wget -q -O Stage/static/libs/chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js
echo "✅ Bibliothèques frontend téléchargées dans Stage/static/libs/"

# ------------------------------
# Interface graphique + VNC (optionnelle mais automatique ici)
# ------------------------------
# INSTALL_GUI="y"
# if [ "$INSTALL_GUI" = "y" ]; then
#   echo "🖥️ Installation interface graphique + VNC..."
#   apt install -y --no-install-recommends raspberrypi-ui-mods realvnc-vnc-server
#   systemctl enable vncserver-x11-serviced
#   systemctl start vncserver-x11-serviced
# fi

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
