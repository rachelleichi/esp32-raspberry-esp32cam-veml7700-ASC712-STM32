import pyb
from time import sleep_ms


# Initialiser le capteur de mouvement
motion_sensor_pin = pyb.Pin('D2', pyb.Pin.IN)

def get_motion():
    motion_detected = motion_sensor_pin.value()  # 1 si mouvement détecté, 0 sinon
    
    
    # Logique pour renvoyer un code basé sur la détection de mouvement et la température
    if motion_detected:  # Si mouvement détecté, renvoyer "11"
        return "11"
    else:
        return "00"  # Pas de mouvement (autre condition)  
