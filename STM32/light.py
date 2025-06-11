import pyb
from time import sleep_ms

light_sensor_pin = pyb.ADC(pyb.Pin('A0'))

last_value = None
repeat_count = 0

while True:
    light_value = light_sensor_pin.read()
    if light_value == last_value:
        repeat_count += 1
    else:
        repeat_count = 0
   

    if repeat_count >= 5:
        print("Erreur : La même valeur se répète 5 fois")
        repeat_count = 0
    
    elif light_value < 200:
        print("Valeur de luminosité : Sombre (<200)")
    else:
        print("Valeur de luminosité : ", light_value)

    last_value = light_value
    sleep_ms(10000)
