import bluetooth # Bibliothèque pour la gestion du BLE
import random # Bibliothèque pour la génération de valeurs aléatoires
from time import sleep_ms # Méthode pour la gestion des temporisations en millisecondes
from ble_advertising import advertising_payload # Méthode pour construire des trames d'advertising
from binascii import hexlify # Méthode pour la conversion binaire vers hexadécimal
from light_s import get_light_value  # Importer la fonction du fichier light_sensor.py
from motion_s import get_motion
import pyb  # Pour accéder à l'RTC et aux broches
# Identifiant de l'advertiser
hex_mac = None

rtc = pyb.RTC()
rtc.datetime((2025, 4, 28, 1, 28, 04, 0, 0))  # Date et heure fixes

# Icône pour une trame GAP environnementale.
_ADV_APPEARANCE_GENERIC_ENVSENSOR = const(5696)

# Classe pour gérer l'advertising de données environnementales
class BLE_Adv_Env:
    # Initialisations
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._connections = set()
        self._handler = None

        # Récupère et enregistre l'adresse MAC de l'objet
        dummy, byte_mac = self._ble.config('mac')
        global hex_mac
        hex_mac = str(hexlify(byte_mac).decode("ascii"))

    # Envoie des trames d'advertising toutes les 10 secondes, précise que l'on ne pourra pas se connecter à l'advertiser
    def advertise(self, interval_us=100000, message=None):
        self._payload = advertising_payload(name=message, services=None, appearance=_ADV_APPEARANCE_GENERIC_ENVSENSOR)
        self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable=False)

# Programme principal
# Initialisations du BLE et du protocole GAP
ble = bluetooth.BLE()
ble_device = BLE_Adv_Env(ble)

while True:
    # Récupérer la valeur de luminosité à partir du fichier light_sensor.py
    light_value = get_light_value()
    motion_value = get_motion()

    # Récupérer la date et l'heure de l'RTC
    current_time = rtc.datetime()
    formatted_time = "{:02d}/{:02d}/{:04d} {:02d}:{:02d}".format(
        current_time[1], current_time[2], current_time[0], current_time[4], current_time[5]
    )

    # Format des données à envoyer via BLE
    strlight = f"{light_value}"
    strmotion = f"{motion_value}"

    # Afficher les valeurs dans le terminal
    print(f"Message diffusé par {hex_mac}")
    print(f" - {strlight} - {strmotion}")

    # Publication en BLE de la luminosité
    ble_device.advertise(message=f"{hex_mac}|{strlight}|{strmotion}")

    # Temporisation de 10 secondes
    sleep_ms(10000)
