
# 📄 **Internship Project Documentation – Raspberry Pi Server and Sensor Monitoring**

## 🖥️ 1. Introduction

This project was carried out as part of my 2nd year internship. It involves deploying a complete environmental monitoring and human presence detection solution using a Raspberry Pi and ESP32 microcontrollers.

---

## 🍓 2. General Architecture

The Raspberry Pi acts as the **central server** that:

* Receives **environmental data (light, current, power)** from an **ESP32 via HTTP**
* Receives **presence detection images** from an **ESP32-CAM**, and uses **YOLOv8** for analysis
* Stores results in a **MariaDB** database
* Hosts a **Flask dashboard** to visualize measurements and generate reports

---

## 📁 3. File Structure

### Home directory `~/`:

```
~/  
├── init.sh                # Installation and Flask servers startup script  
├── grafana.sh             # Grafana startup script  
├── get_ip.sh              # Script to retrieve Raspberry Pi local IP  
├── paquets.txt            # List of Python packages to install  
├── readme.md              # This README file  
├── flask.log              # Flask server logs  
├── venv/                  # Python virtual environment  
└── Stage/                 # Main project folder (details below)  
```

### Directory `~/Stage`:

```
Stage/
├── yolov8.py              # Flask YOLOv8 server – port 5010  
├── dashboard.py           # Flask dashboard – port 5011  
├── weekly_report.py       # Excel report + charts generator  
├── send_email_alert.py    # (optional) Email alert on anomaly  
├── send_report.py         # (optional) Send reports by email  
├── clean.py               # Full database cleanup  
├── clean_db.py            # Targeted database cleanup  
├── monitor_db.py          # Manual DB monitoring (optional)  
|__alert_logs.txt          # Log errors for monitor_db.py  
├── STM32_BLE.py           # Bluetooth communication with STM32  
├── yolov8n.pt             # Pre-trained YOLOv8 model  
├── uploads_yolov8/        # Folder for uploaded images and `status.txt`  
├── templates/  
│   └── dashboard.html     # Flask dashboard HTML page  
├── static/                # Contains generated Excel files and images  
└── models/                # (optional) Additional or archived models  
```

---

## 🔗 4. Connectivity & Network

### 🌐 Creating a Wi-Fi Hotspot on the Raspberry Pi

To enable the PC, ESP32, and ESP32-CAM to communicate with the Raspberry Pi, **connect all devices to the same local Wi-Fi network**. The easiest is to create a **hotspot directly on the Raspberry Pi**.

#### 📡 Manual hotspot creation:

```bash
nmcli dev wifi hotspot ifname wlan0 ssid MyHotspot password mypassword
```

Explanation:

* `wlan0` : Wi-Fi interface
* `MyHotspot` : network name
* `mypassword` : hotspot password

Once the hotspot is active, **connect the PC, ESP32, and ESP32-CAM to it**.
The Raspberry Pi local IP is usually `192.168.43.1` (see section 5).

#### 🔁 Enable hotspot automatically at boot

To activate the hotspot on every reboot:

```bash
nmcli connection modify Hotspot connection.autoconnect yes
```

---

## 🔌 4.1 Connecting a Classic ESP32 to the Hotspot

### 🧰 Required hardware

* 1 **ESP32 DevKit** board
* 1 **micro-USB** cable
* 1 **VEML7700 light sensor** (I2C output)
* 1 **ACS712 30A current sensor** (analog output)

---

### 🖥️ Step 1: Install Arduino IDE

1. Download and install Arduino IDE here:
   👉 [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)
2. Launch the Arduino IDE

---

### ⚙️ Step 2: Add ESP32 boards to the IDE

1. Go to **File > Preferences**
2. In **Additional Boards Manager URLs**, add:

```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

3. Go to **Tools > Board > Boards Manager**
4. Search for "**ESP32**" and install **esp32 by Espressif Systems**

---

### ⚡ Step 3: Connect hardware

* **Plug the ESP32** into the PC via micro-USB
* In Arduino IDE:

  * **Board**: `ESP32 Dev Module`
  * **Port**: auto-selected after plugging in
  * **Baud rate**: 115200

---

### 🔧 Step 4: Connect sensors

#### 🟡 VEML7700 (light)

| VEML7700 | ESP32         |
| -------- | ------------- |
| VIN      | 3.3V          |
| GND      | GND           |
| SDA      | GPIO 21 (SDA) |
| SCL      | GPIO 22 (SCL) |

#### 🔵 ACS712 (current)

Connect to analog PIN A0 or:

| ACS712 | ESP32                  |
| ------ | ---------------------- |
| VCC    | 5V                     |
| GND    | GND                    |
| OUT    | GPIO 34 (analog input) |

---

### 🧠 Step 5: Modify `esp32_veml7700_acs712.ino` code

Open the file and edit lines 22, 23, 24:

```cpp
const char* ssid = "MyHotspot";         // Raspberry Pi hotspot name
const char* password = "mypassword";    // password
const char* serverName = "http://192.168.43.1:5010/data";  // Flask IP + endpoint
```

Make sure the Pi IP address is correct (usually `192.168.43.1` in hotspot mode).

---

### 🚀 Step 6: Upload the code

1. In Arduino IDE, click the **→** (right arrow) button
2. Open the **Serial Monitor** (`Ctrl + Shift + M`) to watch hotspot connection and HTTP requests
3. Connect the ESP32-CAM with micro-USB cable to Raspberry Pi or power source

---

## 📷 4.2 Connecting the ESP32-CAM to the Hotspot

### 🧰 Required hardware

* 1 **ESP32-CAM** board
* 1 **micro-USB** cable (with integrated adapter if your model has it)
* No serial adapter needed if your ESP32-CAM has built-in USB

---

### ⚙️ Step 1: Configure Arduino IDE

* **Board**: `AI Thinker ESP32-CAM`
* **Port**: detected after connection
* **Baud rate**: 115200
* **Flash Mode**: `QIO`

---

### 📁 Step 2: Modify `wifi.ino` code

Change the following lines (lines 8, 10, 11):

```cpp
const char* ssid = "MyHotspot";         // Pi hotspot name
const char* password = "mypassword";    // password
String serverIP = "192.168.43.1";       // Pi IP
```

The file sends photos to URL `http://192.168.43.1:5000/upload` by default.

---

### 🖲️ Step 3: Flash mode

If your board **does not have a built-in flash button**:

1. Start upload (`→`)
2. Connect the ESP32-CAM via micro-USB cable to Raspberry Pi or power source

---

### 🔍 Step 4: Verification

1. Open the **Serial Monitor**
2. You should see a local IP (e.g. `192.168.43.16`) indicating the ESP32-CAM connected to the hotspot
3. The image is captured and sent by POST to your Flask server

---

## 🌍 5. Accessing Flask & Grafana servers

Once all devices are connected to the hotspot:

* Flask dashboard: [http://192.168.X.X:5011](http://192.168.X.X:5011)
* YOLOv8 server: [http://192.168.X.X:5010](http://192.168.X.X:5010)
* Grafana interface: [http://192.168.X.X:3000](http://192.168.X.X:3000)

> Replace `192.168.X.X` with the Raspberry Pi local IP.
> To find it:

```bash
hostname -I
```

or:

```bash
./get_ip.sh
```

---

## 🧠 6. YOLOv8 – Presence Detection (`yolov8.py`)

* Flask – Port 5010
* Receives images `POST /uploads` (field: `imageFile`)
* Receives data `POST /data`: `lux`, `current`, `power`
* Saves data in MariaDB (table `presence`)
* Writes a `status.txt`
* Saves images with suffix `presence_0` or `presence_1`

---

## 📊 7. Dashboard – Data Visualization (`dashboard.py`)

* **Flask** – Port 5011
* Displays charts for the three tables: `presence`, `luminosity`, `intensity`
* Date filters (`start_date`, `end_date`)
* Excel download available

---

## 📈 8. Weekly Report (`weekly_report.py`)

* Connects to MariaDB
* Retrieves the last 7 days of data
* Generates:

  * Histograms: presence, luminosity
  * Line charts: current, power
* Outputs an Excel file and PNG images saved in `static/`

---

## 🧽 9. Database Cleanup (`clean_db.py`)

* Targeted data deletion modes:

  * `day` mode or `last_n` mode
* Useful for testing or reducing database size

---

## 🔐 10. MariaDB Database

* **User**: `rachel`
* **Password**: `Stage.2025`
* **Database**: `Stage`

### Tables:

* `presence(timestamp, presence_detected)`
* `luminosity(timestamp, lux_level)`
* `intensity(timestamp, current, power)`

---

## ▶️ 11. Execution – Complete Guide

### 🔧 Prerequisites

* Raspberry Pi with **Python 3.9+**
* Internet access to download packages
* Scripts `init.sh` and `grafana.sh` located in `~/`

### ✅ Automatic Launch

1. **Install & start the servers**:

   ```bash
   sudo chmod +x init.sh
   sudo ./init.sh
   ```

2. **Start Grafana**:

   ```bash
   sudo chmod +x grafana.sh
   sudo ./grafana.sh
   ```

3. **Generate the report**:

   ```bash
   cd ~/Stage
   python3 weekly_report.py
   ```

4. **Clean the database**:

   ```bash
   python3 clean_db.py
   ```

---

## 🐍 12. Manual Virtual Environment Setup (if `init.sh` fails)

1. **Create and activate** the virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install required packages** (see `paquets.txt`):

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

3. **Manually start the servers**:

   ```bash
   python3 yolov8.py       # Port 5010
   python3 dashboard.py    # Port 5011
   sudo systemctl start grafana-server  # Port 3000
   ```

---

## 🕒 13. Automations with `crontab`

### 📅 13.1 Weekly Report Automation

To automatically generate the weekly report every **Monday at 8 AM**, edit the `crontab` for user `pi` (or your main user):

```bash
crontab -e
```

Add at the bottom:

```bash
0 8 * * 1 cd /home/pi/Stage && /home/pi/venv/bin/python3 weekly_report.py >> /home/pi/Stage/cron_report.log 2>&1
```

* `0 8 * * 1`: runs every Monday at 08:00
* `cd /home/pi/Stage`: navigates to the project folder
* `/home/pi/venv/bin/python3`: uses the virtual environment’s Python
* `>> … 2>&1`: redirects output and errors to `cron_report.log`

*Adjust `/home/pi` to your actual username if different.*

---

### 🧠 13.2 Auto-start `init.sh` on Reboot

To run `init.sh` automatically in the background on every reboot, add:

```bash
crontab -e
```

Then add:

```bash
@reboot /home/pi/init.sh >> /home/pi/init.log 2>&1
```

---

## 🧰 14. Raspberry Pi Setup (Desktop OS + Initial Configuration)

### 📦 Step 1: Download Raspberry Pi Imager

1. Go to:
   👉 [https://www.raspberrypi.com/software](https://www.raspberrypi.com/software)
2. Download and install **Raspberry Pi Imager** (Windows, macOS, or Ubuntu)

---

### 🖥️ Step 2: Prepare the microSD Card

1. Insert a **16 GB (or larger) microSD card** into your computer
2. Launch **Raspberry Pi Imager**
3. Select:

   * **OS**: `Raspberry Pi OS with desktop (32-bit)`
   * **Storage**: your microSD card
4. Click the ⚙️ icon (bottom right) to preconfigure:

   * Hostname (e.g., `raspberrypi`)
   * Username (e.g., `pi`)
   * Password
   * Enable SSH
   * Wi-Fi SSID & password (if you want to preconnect)
   * Timezone and keyboard layout
5. Click **Write** and wait

---

### 🔌 Step 3: Boot the Raspberry Pi

1. Insert the microSD card into the Pi
2. Connect an HDMI monitor, keyboard, and mouse (optional after first boot)
3. Power on the Pi
4. Optionally, SSH in if network and SSH are configured:

   ```bash
   ssh pi@<raspberry-pi-ip>
   ```

---

### ⚙️ Step 4: Update the System

```bash
sudo apt update && sudo apt upgrade -y
```

---

### 🛠️ Step 5: Install Required Tools

Now you can clone the project, run `init.sh`, create the hotspot, etc., following section 11:

```bash
git clone https://github.com/rachelleichi/esp32-raspberry-esp32cam-veml7700-ASC712-STM32.git
```

*Note: The STM32 and `STM32_BLE.py` parts are not covered in this README, as they were not needed for the internship.*

