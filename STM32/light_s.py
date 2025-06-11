import pyb
from time import sleep_ms

# Initialiser le capteur de lumière
light_sensor_pin = pyb.ADC(pyb.Pin('A0'))

# Variables pour gérer la répétition de la valeur
last_value = None
repeat_count = 0

def get_light_value():
    global last_value, repeat_count
    
    # Lire la valeur de luminosité
    light_value = light_sensor_pin.read()

    # Vérifier si la valeur est la même que la précédente
    if light_value == last_value:
        repeat_count += 1
    else:
        repeat_count = 0

    # Si la même valeur se répète 5 fois
    if repeat_count >= 5:
        return "000"  # Code "00" pour répétition 5 fois
    # Si la luminosité est inférieure à 200
    elif light_value <= 200:
        return "0"  # Code "0" pour luminosité faible (<200)
    else:
        return str(light_value)  # Retourner la valeur de la luminosité

    last_value = light_value
