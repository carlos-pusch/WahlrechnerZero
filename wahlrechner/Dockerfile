FROM python:3.12

RUN mkdir /code
WORKDIR /code

# 1. Nur die requirements.txt kopieren (damit der nächste Layer nur bei Änderungen neu läuft)
COPY requirements.txt /code/

# 2. Pakete installieren (pip upgraden + Abhängigkeiten)
RUN pip install --upgrade pip && pip install -r requirements.txt

# 3. Jetzt den restlichen Code kopieren
COPY . /code/

# 4. Berechtigungen für die Skripte setzen (nachdem sie vorhanden sind)
RUN chmod +x /code/docker/startup.sh
RUN chmod +x /code/docker/startup-production.sh
RUN chmod +x /code/docker/wait-for-it/wait-for-it.sh

# 5. static-Verzeichnis anlegen
RUN mkdir /static/

EXPOSE 80
