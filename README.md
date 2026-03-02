# WahlrechnerZero

**Die Ursprungsversion stammte von [Linus Köster](https://github.com/wahlrechner/wahlrechner) mit Stand von August 2024, aber wurde unabhängig weiterentwickelt**
<li>Multi-Tenant Unterstützung</li>
<li>Hintergrundinfobutton eingebaut</li>
<li>eigenes Thesenseitenmenu bei mobiler Ansicht eingefügt</li>
<li>Möglichkeit zur De-/ Aktivierung von einzelnen Wahlen eingebaut</li>
<li>"Bald verfügbar" Meldung eingebaut (für bereits hinterlegte, aber inaktive Wahlen)</li>
<li>"Unbekannt" Meldung eingebaut (für noch nicht hinterlegte Wahlen)</li>
<li>Editierbare ausgewählte Einträge im Admin-Interface</li>
<li>Dockerfile bzgl. Package Installationen effizienter eingerichtet</li>
<li>CSS für eigene Bedürfnisse angepasst</li>
<li>docker/wait-for-it lokal ergänzt</li>

# Aufsetzen eines Wahlrechner-Servers

Dieses Repository dient als Hifestellung, um eine [Wahlrechner](https://github.com/wahlrechner/wahlrechner)-Instanz auf einem Server inkl. Host aufzusetzen.
Die folgende Anleitung funktioniert nur auf Debian-basierten Systemen, und wurde ausschließlich mit `Ubuntu 24.04 LTS` getestet.

## Vorraussetzungen

### Installation von Git

```
sudo apt update && sudo apt install git -y
```

### Repository klonen

Achtung der hier verwendete Code ist hier zwar richtig, aber für den produktiven Einsatz (mit Annahme von installierten Docker und Caddy) besser in der *Kurzanleitung.md* dokumentiert.

```
sudo mkdir /Wahlrechner
sudo git clone --recurse-submodules https://github.com/carlos-pusch/WahlrechnerZero /Wahlrechner
cd /Wahlrechner
```

### Installation von Docker

Einschub: Falls mal Probleme mit Schreibrechten durch `docker compose up -d` entstehen, dann liegt es vermutlich an docker-snap.
Stattdessen muss docker-ce verwendet werden. Ggf. folgenden Code zum Entfernen verwenden:

```
sudo snap remove docker --purge
```

_Mehr Informationen zur Installation von Docker findest du [hier](https://docs.docker.com/engine/install/ubuntu/)._

```
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
```

```
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Konfiguration des Wahlrechners

Durchführung s. Kurzanleitung mit Skript zum Runterladen

**DJANGO_SECRET_KEY:** Ersetze `ChangeThisToRandomStringInProduction` durch eine [zufällig generierte](https://1password.com/de/password-generator/) (mind. 30 Zeichen lang, bestehend aus Zahlen, Buchstaben und Sonderzeichen) Zeichenkette. Teile den Secret Key niemals mit jemand anderem!

**DJANGO_DEFAULT_ADMIN_PASSWORD:** Beim erstmaligen Starten des Wahlrechners wird automatisch ein Admin-Account erstellt. Ersetze das Dummypasswort durch ein erstes, sicheres Passwort.

**MYSQL_PASSWORD:** Ersetze `SetDatabaseUserPassword` durch ein zufällig generiertes Passwort. Du wirst es niemals von Hand eingeben müssen - also lass dir bitte ein sicheres Passwort mit einem [Passwortgenerator](https://1password.com/de/password-generator/) generieren.
