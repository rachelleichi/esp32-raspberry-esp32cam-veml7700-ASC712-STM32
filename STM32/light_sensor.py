import pyb
from time import sleep_ms

light_sensor_pin = pyb.ADC(pyb.Pin('A0'))

last_value = None
repeat_count = 0

rtc = pyb.RTC()
rtc.datetime((2025, 4, 28, 1, 13, 52, 0, 0))

while True:
    light_value = light_sensor_pin.read()
    
    # Récupérer l'heure et la date de l'RTC
    current_time = rtc.datetime()
    formatted_time = "{:02d}/{:02d}/{:04d} {:02d}:{:02d}".format(current_time[1], current_time[2], current_time[0], current_time[4], current_time[5])

    if light_value == last_value:
        repeat_count += 1
    else:
        repeat_count = 0

    if repeat_count >= 5:
        print(f"{formatted_time} - Erreur : La même valeur se répète 5 fois")
        repeat_count = 0
    
    elif light_value <= 200:
        print(f"{formatted_time} - Valeur de luminosité : sombre (<200)")
    else:
        print(f"{formatted_time} - Valeur de luminosité : {light_value}")

    last_value = light_value
    sleep_ms(10000)
