# Cet exemple montre comment programmer un advertiser BLE avec la technologie Bluetooth SIG
# pour publier des mesures de température et d'humidité en mode (GAP).
# Les mesures sont simulées avec un générateur de nombres aléatoires toutes les cinq secondes.
# Les advertisers signalent leur identité en diffusant leur adresse MAC.

import bluetooth # Bibliothèque pour la gestion du BLE
import random # Bibliothèque pour la génération de valeurs aléatoires
from time import sleep_ms # Méthode pour la gestion des temporisations en millisecondes
from ble_advertising import advertising_payload # Méthode pour construire des trames d'advertising
from binascii import hexlify # Méthode pour la conversion binaire vers hexadécimal

# Identifiant de l'advertiser
hex_mac = None

# Icône pour une trame GAP environnementale.
# Voir org.bluetooth.characteristic.gap.appearance.xml
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

    # Envoie des trames d'advertising toutes les 5 secondes, précise que l'on ne pourra pas se connecter à l'advertiser
      def advertise(self, interval_us=500000, message = None):
         self._payload = advertising_payload(name=message, services=None, appearance=_ADV_APPEARANCE_GENERIC_ENVSENSOR)
            self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable = False)

# Programme principal

# Initialisations du BLE et du protocole GAP
ble = bluetooth.BLE()
ble_device = BLE_Adv_Env(ble)

while True:

  # Mesures (simulées)
   temperature = random.randint(-20, 90) # Valeur aléatoire entre -20 et 90 (supposément en °C)
  humidity = random.randint(0, 100) # Valeur aléatoire entre 0 et 100 (supposément en %)
       
        stemperature = str(temperature)
      shumidity = str(humidity)
  
   print("Message diffusé par " + hex_mac)
       print(" - Température (°C) : " + stemperature)
        print(" - Humidité relative (%) : " + shumidity)
 
  # Publication en BLE de la température et de l'humidité
      ble_device.advertise(message = hex_mac + "|" + stemperature + "|" + shumidity)

     # Temporisation de cinq secondes
      sleep_ms(5000)
