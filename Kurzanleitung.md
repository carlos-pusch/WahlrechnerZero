### Kurzanleitung

Im Terminal

```python
dir_name="Wahlrechner"
sudo mkdir $dir_name

sudo git clone https://github.com/carlos-pusch/WahlrechnerZero "$dir_name"

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

docker compose down; docker compose build; docker compose up -d

[//]: # Ggf. einen anderen Dienst wegen gleichen Port schließen
[//]: # oder caddy stop ausführen 

```
