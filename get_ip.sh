#!/bin/bash

# Récupérer l'adresse IP de l'interface wlan0
IP=$(ip -4 addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

# Vérifier si une IP a été trouvée
if [ -n "$IP" ]; then
    echo "Adresse IP de wlan0 : $IP"
else
    echo "Aucune adresse IP trouvée sur wlan0."
fi
