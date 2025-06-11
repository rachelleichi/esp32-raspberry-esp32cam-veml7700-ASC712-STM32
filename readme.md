
# 📄 **Documentation du Projet de Stage – Serveur Raspberry Pi et Surveillance par Capteurs**

## 🖥️ 1. Introduction

Ce projet a été réalisé dans le cadre de mon stage de fin d'année. Il consiste à déployer une solution complète de surveillance environnementale et de détection de présence humaine à l’aide d’un Raspberry Pi et de microcontrôleurs ESP32.

---

## 🍓 2. Architecture générale

Le Raspberry Pi agit comme **serveur central** qui :

* Reçoit des **données environnementales (luminosité, courant, puissance)** depuis un **ESP32 via HTTP**
* Reçoit des **images de détection de présence** depuis une **ESP32-CAM**, et utilise **YOLOv8** pour les analyser
* Stocke les résultats dans une base de données **MariaDB**
* Héberge un **dashboard Flask** pour visualiser les mesures et générer des rapports

---

## 📁 3. Arborescence des fichiers

### Répertoire personnel `~/` :

```
~/
├── init.sh                # Script d'installation et de lancement des serveurs Flask
├── grafana.sh             # Script de démarrage de Grafana
├── get_ip.sh              # Script pour récupérer l'IP locale du Raspberry Pi
├── paquets.txt            # Liste des paquets Python à installer
├── readme.md              # Ce fichier README
├── flask.log              # Logs du serveur Flask
├── venv/                  # Environnement virtuel Python
└── Stage/                 # Dossier principal du projet (détail ci-dessous)
```

### Répertoire `~/Stage` :

```
Stage/
├── yolov8.py              # Serveur Flask YOLOv8 – port 5010
├── dashboard.py           # Dashboard Flask – port 5011
├── weekly_report.py       # Générateur de rapport Excel + graphiques
├── send_email_alert.py    # (optionnel) Alerte email en cas d'anomalie
├── send_report.py         # (optionnel) Envoi de rapports par email
├── clean.py               # Nettoyage total de la base
├── clean_db.py            # Nettoyage ciblé de la base de données
├── monitor_db.py          # Monitoring manuel de la base (optionnel)
|__alert_logs.txt          # Ecriture des erreurs de logs du  script monitor_db.py
├── STM32_BLE.py           # Communication Bluetooth avec le STM32
├── yolov8n.pt             # Modèle YOLOv8 pré-entraîné
├── uploads_yolov8/        # Dossier pour images uploadées et `status.txt`
├── templates/
│   └── dashboard.html     # Page HTML du dashboard Flask
├── static/                # Contient les fichiers Excel et images générés
└── models/                # (optionnel) Modèles supplémentaires ou archives
```

---

## 🔗 4. Connectivité & Réseau

### 🌐 Créer un hotspot Wi-Fi sur le Raspberry Pi

Afin que le PC, l’ESP32 et l’ESP32-CAM puissent communiquer avec le Raspberry Pi, **connectez tous les appareils au même réseau Wi-Fi local**. Le plus simple est de créer un **hotspot directement depuis le Raspberry Pi**.

#### 📡 Création manuelle du hotspot :

```bash
nmcli dev wifi hotspot ifname wlan0 ssid MonHotspot password monmotdepasse
```
explications :
* `wlan0` : interface Wi-Fi
* `MonHotspot` : nom du réseau
* `monmotdepasse` : mot de passe du hotspot

Une fois le hotspot activé, **connectez-y le PC, l’ESP32 et l’ESP32-CAM**.
L'adresse IP locale du Raspberry Pi est généralement `192.168.**.1`. (partie 5)

#### 🔁 Activer le hotspot automatiquement au démarrage

Pour activer le hotspot à chaque démarrage :

```bash
nmcli connection modify Hotspot connection.autoconnect yes
```

---

## 🔌 4.1 Connexion de l’ESP32 Classique au Hotspot

### 🧰 Matériel nécessaire

* 1 carte **ESP32 DevKit**
* 1 câble **micro-USB**
* 1 capteur de **luminosité VEML7700 (sortie I2C)**
* 1 capteur de **courant ACS712 30A (sortie analogique)**

---

### 🖥️ Étape 1 : Installer l’IDE Arduino

1. Télécharger et installer l’IDE Arduino ici :
   👉 [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)

2. Lancer l’IDE Arduino

---

### ⚙️ Étape 2 : Ajouter les cartes ESP32 dans l’IDE

1. Aller dans **Fichier > Préférences**
2. Dans **URL de gestionnaire de cartes supplémentaires**, ajouter :

```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

3. Aller dans **Outils > Type de carte > Gestionnaire de cartes**
4. Rechercher "**ESP32**" et installer **esp32 by Espressif Systems**

---

### ⚡ Étape 3 : Connexion du matériel

* **Brancher l’ESP32** au PC avec le câble micro-USB
* Dans l’IDE Arduino :

  * **Carte** : `ESP32 Dev Module`
  * **Port** : sélection automatique après branchement
  * **Vitesse** : 115200

---

### 🔧 Étape 4 : Connexion des capteurs

#### 🟡 VEML7700 (luminosité)

| VEML7700 | ESP32         |
| -------- | ------------- |
| VIN      | 3.3V          |
| GND      | GND           |
| SDA      | GPIO 21 (SDA) |
| SCL      | GPIO 22 (SCL) |

#### 🔵 ACS712 (intensité)

Le connecter au PIN analogique A0

ou bien :

| ACS712 | ESP32                       |
| ------ | --------------------------- |
| VCC    | 5V                          |
| GND    | GND                         |
| OUT    | GPIO 34 (entrée analogique) |


---

### 🧠 Étape 5 : Modifier le code `esp32_veml7700_acs712.ino`

Ouvrir le fichier et modifier les lignes 22,23,24 :

```cpp
const char* ssid = "MonHotspot";         // nom du hotspot du Raspberry Pi
const char* password = "monmotdepasse";  // mot de passe
const char* serverName = "http://192.168.43.1:5010/data";  // IP + endpoint Flask
```

Assurez-vous que l’adresse IP du Pi est correcte (souvent `192.168.43.1` en hotspot).

---

### 🚀 Étape 6 : Téléverser le code

1. Dans l’IDE Arduino, cliquez sur le bouton **→** (flèche droite)
2. Ouvrez le **Moniteur série** (`Ctrl + Maj + M`) pour suivre la connexion au hotspot et les requêtes HTTP
3. Lier L'ESP32 cam par le cable micro usb au raspberry ou a une alimentation

---

## 📷 4.2 Connexion de l’ESP32-CAM au Hotspot

### 🧰 Matériel nécessaire

* 1 carte **ESP32-CAM**
* 1 câble **micro-USB** (avec adaptateur intégré si votre modèle le permet)
* Pas besoin d’adaptateur série si vous avez un module ESP32-CAM avec USB intégré

---

### ⚙️ Étape 1 : Paramétrer l’IDE Arduino

* **Carte** : `AI Thinker ESP32-CAM`
* **Port** : détecté après branchement
* **Vitesse** : 115200
* **Flash Mode** : `QIO`

---

### 📁 Étape 2 : Modifier le code `wifi.ino`

Changer les lignes suivantes (lignes 8,10 et 11) :

```cpp
const char* ssid = "MonHotspot";         // nom du hotspot du Pi
const char* password = "monmotdepasse";  // mot de passe
String serverIP = "192.168.43.1";        // IP du Pi
```

Le fichier envoie des photos à l’URL `http://192.168.43.1:5000/upload` par défaut.

---

### 🖲️ Étape 3 : Mode flash

Si votre carte **n’a pas de bouton de flash intégré** :

1. Lancer le téléversement (`→`)
2. Lier L'ESP32 cam par le cable micro usb au raspberry ou a une alimentation


---

### 🔍 Étape 4 : Vérification

1. Ouvrir le **Moniteur série**
2. Vous devriez voir une IP locale (ex. `192.168.43.16`) indiquant que l’ESP32-CAM s’est connecté au hotspot
3. L’image est capturée puis envoyée en POST à votre serveur Flask




## 🌍 5. Accéder aux serveurs Flask & Grafana

Une fois tous les appareils connectés au hotspot :

* Dashboard Flask : [http://192.168.X.X:5011](http://192.168.X.X:5011)
* Serveur YOLOv8 : [http://192.168.X.X:5010](http://192.168.X.X:5010)
* Interface Grafana : [http://192.168.X.X:3000](http://192.168.X.X:3000)

> Remplace `192.168.X.X` par l’adresse IP locale du Raspberry Pi.
> Pour la connaître :

```bash
hostname -I
```

Ou :

```bash
./get_ip.sh
```

---

## 🧠 6. YOLOv8 – Détection de Présence (`yolov8.py`)

* Flask – Port 5010
* Reçoit images `POST /uploads` (champ : `imageFile`)
* Reçoit données `POST /data` : `lux`, `current`, `power`
* Sauvegarde dans MariaDB (table `presence`)
* Écrit aussi un `status.txt`
* Enregistre les images avec suffixe `presence_0` ou `presence_1`

---

## 📊 7. Dashboard – Visualisation des Données (`dashboard.py`)

* Flask – Port 5011
* Affiche graphiques des 3 tables : `presence`, `luminosite`, `intensite`
* Filtres par date (`start_date`, `end_date`)
* Téléchargement Excel possible

---

## 📈 8. Rapport Hebdomadaire (`weekly_report.py`)

* Connexion à MariaDB
* Récupère les 7 derniers jours
* Génère :

  * Histogrammes : présence, luminosité
  * Courbes : courant, puissance
* Fichier Excel + images PNG enregistrés dans `static/`

---

## 🧽 9. Nettoyage de la Base (`clean_db.py`)

* Suppression ciblée des données

  * Mode `day` ou `last_n`
* Pour tests ou allègement

---

## 🔐 10. Base de Données MariaDB

* Utilisateur : `rachel`
* Mot de passe : `Stage.2025`
* Base : `Stage`

### Tables :

* `presence(timestamp, presence_detected)`
* `luminosite(timestamp, taux_luminosite)`
* `intensite(timestamp, courant, puissance)`

---

## ▶️ 11. Exécution – Guide Complet

### 🔧 Prérequis

* Raspberry Pi avec Python 3.9+
* Internet pour télécharger les paquets
* Scripts `init.sh` et `grafana.sh` dans `~/`

### ✅ Lancement Automatique

1. 📦 Installation & démarrage des serveurs :

```bash
sudo chmod +x init.sh
sudo ./init.sh
```

2. 🌐 Démarrage de Grafana :

```bash
sudo chmod +x grafana.sh
sudo ./grafana.sh
```

3. 📊 Génération de rapport :

```bash
cd /Stage
python3 weekly_report.py
```

4. 🧹 Nettoyage de la base :

```bash
python3 clean_db.py
```

---

## 🐍 12. Installation Manuelle de l'environement virtuel (si erreur du script init.sh)

1. Créer et activer l’environnement virtuel :

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Installer les paquets :

Contenu du `paquets.txt` :

```
Flask==2.3.2
numpy==1.25.2
opencv-python-headless==4.8.0.74
ultralytics==8.0.134
torch==2.0.1
pyserial
mysql-connector-python
openpyxl
```

```bash
pip install -r paquets.txt
```

3. Lancer manuellement les serveurs :

```bash
python3 yolov8.py       # Port 5010
python3 dashboard.py    # Port 5011
sudo systemctl start grafana-server  # Port 3000
```

---
Voici une **nouvelle section 13** que vous pouvez **ajouter à la fin de votre documentation** pour automatiser la génération de rapports hebdomadaires et lancer automatiquement le script `monitor_db.py` au démarrage via `cron` :

---

## 🕒 13. Automatisations avec `crontab`

### 📅 13.1 Génération automatique du rapport chaque semaine

Pour générer automatiquement le rapport hebdomadaire chaque **lundi à 8h du matin**, ajoutez une tâche dans la `crontab` de l'utilisateur `pi` (ou votre utilisateur principal) :

```bash
crontab -e
```

Ajoutez la ligne suivante tout en bas du fichier :

```bash
0 8 * * 1 cd /home/pi/Stage && /home/pi/venv/bin/python3 weekly_report.py >> /home/pi/Stage/cron_report.log 2>&1
```

Explications :

* `0 8 * * 1` : exécution chaque lundi à 08:00
* `cd /home/pi/Stage` : on se place dans le dossier du projet
* `/home/pi/venv/bin/python3` : exécute le script avec l’environnement virtuel Python
* `>> ... 2>&1` : log de sortie et d'erreur redirigé dans `cron_report.log`

🔧 **Adaptez le chemin `/home/pi` à votre utilisateur si besoin, avec rachel le nom d'utilisateur**

---

### 🧠 13.2 Démarrage automatique du script `init.sh`

Pour lancer en **tâche de fond à chaque redémarrage**, ajoutez une ligne dans la `crontab` avec l’option `@reboot` :

```bash
crontab -e
```

Puis ajoutez :

```bash
@reboot /home/pi/init.sh >> /home/pi/init.log 2>&1
```

Voici la section à ajouter à la fin de ton README pour expliquer comment configurer un Raspberry Pi depuis zéro avec un système d’exploitation Desktop :

---

## 🧰 14. Mise en route d’un Raspberry Pi (OS Desktop + configuration initiale)

### 📦 Étape 1 : Télécharger Raspberry Pi Imager

1. Va sur le site officiel :
   👉 [https://www.raspberrypi.com/software](https://www.raspberrypi.com/software)

2. Télécharge et installe **Raspberry Pi Imager** (disponible pour Windows, macOS, Ubuntu)

---

### 🖥️ Étape 2 : Préparer la carte microSD

1. Insère une **carte microSD (16 Go ou +)** dans ton ordinateur
2. Lance **Raspberry Pi Imager**
3. Choisis :

   * **OS** : `Raspberry Pi OS with desktop (32-bit)`
   * **Stockage** : ta carte microSD
4. Clique sur ⚙️ (roue dentée en bas à droite) pour **préconfigurer** :

   * Nom de l’hôte (ex. `raspberrypi`)
   * Nom d’utilisateur (ex. `pi`)
   * Mot de passe
   * Activer SSH
   * Configurer le Wi-Fi (SSID + mot de passe) – ou ignorer si tu veux créer un hotspot après
   * Choisir le fuseau horaire
5. Clique sur **Écrire** et patiente

---

### 🔌 Étape 3 : Démarrer le Raspberry Pi

1. Insère la carte microSD dans le Raspberry Pi
2. Branche un écran, un clavier/souris et le câble d’alimentation
3. Le Raspberry Pi démarre automatiquement

> Si tu as activé SSH + Wi-Fi, tu peux aussi te connecter à distance sans écran avec :

```bash
ssh pi@<adresse-ip>
```
en etant sur le meme réseau
---

### ⚙️ Étape 4 : Mettre à jour le système

Ouvre un terminal et exécute :

```bash
sudo apt update && sudo apt upgrade -y
```

---

### 🛠️ Étape 5 : Installer les outils nécessaires

Tu peux maintenant cloner ton projet, lancer le script `init.sh`, créer un hotspot, etc.

Exemple :

```bash
git clone https://github.com/rachelleichi/esp32-raspberry-esp32cam-veml7700-ASC712-STM32.git
cd ~/Stage
chmod +x ~/init.sh
./init.sh
```

