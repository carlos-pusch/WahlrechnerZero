# WahlrechnerZero

**Die Ursprungsversion stammte von [Linus Köster](https://github.com/wahlrechner/wahlrechner) mit seinem Stand von August 2024, aber wurde unabhängig weiterentwickelt**
<ul>
  <li>Umgesetzte Änderungen
    <ul>
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
      <li>Zentraler Wartungszustand per Admin Interface aktivierbar</li>
    </ul>
  </li>
  <li>Mögliche Änderungen
    <ul>
      <li>in Einarbeitung: Freitext Antworten nach dem / außerhalb des quantifizierbaren Wahlchecks darstellen</li>
      <li>in Einarbeitung: Einbindung von Grafiken zur Bewertung der Kandidierenden durch die Positionierung bei den klimapositiven Thesen</li>
      <li>in Umsetzung: vor dem eigentlichen Start Kurzvorstellung des lokalen Teams und die Darstellung der Übersicht der nicht geantworteten Kandidierenden</li>
      <li>in Umsetzung: Einbindung von Grafiken zur Bewertung der Kandidierenden durch die Positionierung bei den klimapositiven Thesen</li>
      <li>to-do: Direkter Vergleich von 3 Kandidierenden / Parteien mit detaillierte Auswertung, wo Unterschiede sind</li>
      <li>to-do: Link teilen Funktion (nach dem Motto "ich habe den Wahlcheck gemacht, du auch?)</li>
      <li>in Planung: Einbau von Klimadatenanalysen runtergeschnitten auf geografische Bereiche der Wahlkreise oder Landkreise</li>
      <li>in Planung: Möglichkeit des Exports der eigenen Abstimmungen als PDF oder SharePics</li>
      <li>zu prüfen: Feedback-Mechanismus - Nutzer:innen können melden, wenn eine These oder Antwort unklar oder irreführend ist</li>
      <li>zu prüfen: aktuelle Antworten im Vergleich mit den Wahlkreisabstimmungen / Statistik darstellen</li>
      <li>zu prüfen: Vorlesefunktion per Browser-API, https://developer.mozilla.org/de/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API</li>
      <li>zu prüfen: Kommentar-/ Diskussionsfunktion pro These durch die Besucher:innen</li>
    </ul>
  </li>
</ul>

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

Einschub: Es sollte kein docker-snap verwendet werden.
Stattdessen sollte docker-ce verwendet werden. Ggf. folgenden Code zum Entfernen verwenden:

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
