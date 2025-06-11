# Ajout de la clé GPG
sudo apt install -y software-properties-common
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/grafana.gpg

# Ajout du dépôt
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Installation
sudo apt update
sudo apt install -y grafana

# Activation + démarrage
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
