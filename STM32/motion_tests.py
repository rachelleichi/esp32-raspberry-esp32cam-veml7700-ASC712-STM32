import pyb
from time import sleep_ms
import time

# Configurer l'horloge RTC (si l'horloge n'est pas encore définie)
# Définir la date et l'heure actuelle (année, mois, jour, heures, minutes, secondes)
rtc = pyb.RTC()
rtc.datetime((2025, 4, 28, 1, 13, 49, 0, 0))  # Exemple : 28 avril 2025, 12:00:00

# Configurer la broche D2 en mode entrée
motion_sensor_pin_TM2291 = pyb.Pin('D2', pyb.Pin.IN)
motion_sensor_pin_digital = pyb.Pin('D4', pyb.Pin.IN)
#motion_sensor_pin_mini = pyb.Pin('D8', pyb.Pin.IN)


while True:
   # motion_detected = motion_sensor_pin.value()  # 1 si mouvement détecté, 0 sinon
    motion_TM2291 = motion_sensor_pin_TM2291.value()  # 1 si mouvement détecté, 0 sinon
    motion_digital = motion_sensor_pin_digital.value()  # 1 si mouvement détecté, 0 sinon
    #motion_mini = motion_sensor_pin_mini.value()  # 1 si mouvement détecté, 0 sinon


    # Récupérer la date et l'heure actuelle
    current_time = rtc.datetime()
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        current_time[0], current_time[1], current_time[2],
        current_time[4], current_time[5], current_time[6]
    )

    print(f"[{formatted_time}]")
    print(f"Capteur TM2291 : {'Mouvement détecté' if motion_TM2291 else 'Pas de mouvement'}")
    print(f"Capteur Numérique : {'Mouvement détecté' if motion_digital else 'Pas de mouvement'}")
    #print(f"Capteur MINI : {'Mouvement détecté' if motion_mini else 'Pas de mouvement'}")
    print("-" * 30)

    #if motion_detected:
        #print(f"[{formatted_time}] Mouvement détecté !")
    #else:
        #print(f"[{formatted_time}] Pas de mouvement.")

    sleep_ms(10000)  # Pause 10 secondes
