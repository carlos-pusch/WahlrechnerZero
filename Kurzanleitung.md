### Kurzanleitung mit fertigen Code zum Erstart

Im Terminal und kann dann in einem Rutsch ausgeführt werden.

```python
dir_name="Wahlrechner"
sudo mkdir $dir_name

sudo git clone https://github.com/carlos-pusch/WahlrechnerZero "$dir_name"
# falls spezifischer Branch; stattdessen
# sudo git clone -b NAME https://github.com/carlos-pusch/WahlrechnerZero.git "$dir_name"

cd "$dir_name"
cd wahlrechner_host

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker compose down --volumes --remove-orphans
docker network prune

cd .. ; cd wahlrechner

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker compose down --volumes --remove-orphans
docker network prune

cd .. ; cd ..
sudo chmod -R u+rwx "$dir_name"
sudo chmod -R g+rwx "$dir_name"

sudo chown -R carlos:carlos "$dir_name"

cd $dir_name ; cd wahlrechner

docker compose down; docker compose build; docker compose up -d

cd ..; cd wahlrechner_host

echo "";echo "";echo ""

echo "Bist du da?"
read -p "Weiter mit Enter..."
echo "Wurde die Datei 'wahlrechner_host/caddy/caddy.env' angepasst (ROOT_DOMAIN)?"
read -p "Weiter mit Enter..."
echo "Wurde die Datei 'wahlrechner_host/config/config.env' angepasst (DJANGO_DEFAULT_ADMIN_USERNAME)?"
read -p "Weiter mit Enter..."
echo "Wurde die Datei 'wahlrechner_host/config/config.env' angepasst (DJANGO_DEFAULT_ADMIN_PASSWORD)?"
read -p "Weiter mit Enter..."

docker compose down; docker compose build; docker compose up -d

[//]: # Ggf. einen anderen Dienst wegen gleichen Port schließen
[//]: # oder caddy stop ausführen 

```
