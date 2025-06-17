#!/bin/bash

echo "📁 Passage dans le dossier Stage..."
cd /home/rachel/esp32-raspberry-esp32cam-veml7700-ASC712-STM32/Stage || exit 1

echo "🐍 Activation de l'environnement virtuel..."
source ../venv/bin/activate