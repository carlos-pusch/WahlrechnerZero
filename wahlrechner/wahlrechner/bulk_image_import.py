# lz_c_1: Hilfsfunktionen für den Bulk-Image-Import
import os
from django.conf import settings
from .models import Partei

def find_partei_by_filename(filename):
    """
    Durchsucht alle Parteien nach einem Bilddateinamen,
    der mit dem Basename des `partei_bild`-Feldes übereinstimmt.
    Groß-/Kleinschreibung wird ignoriert.
    """
    for partei in Partei.objects.all():
        if partei.partei_bild and os.path.basename(partei.partei_bild.name).lower() == filename.lower():
            return partei
    return None

def save_uploaded_image(uploaded_file, partei):
    """
    Speichert die hochgeladene Datei unter dem in `partei.partei_bild` definierten Pfad.
    Gibt ein Tupel zurück: (erfolg, ziel_relativ, fehlermeldung)
    """
    if not partei.partei_bild:
        return False, None, "Partei hat kein Bildfeld gesetzt"

    target_relative = partei.partei_bild.name   # z.B. "partei_bild/spd_logo.jpg"
    target_absolute = os.path.join(settings.MEDIA_ROOT, target_relative)

    # Prüfen, ob Datei bereits existiert
    if os.path.exists(target_absolute):
        return False, target_relative, "Datei existiert bereits"

    # Zielverzeichnis anlegen (falls nötig)
    os.makedirs(os.path.dirname(target_absolute), exist_ok=True)

    # Datei in Blöcken schreiben
    try:
        with open(target_absolute, 'wb') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        return True, target_relative, None
    except Exception as e:
        return False, target_relative, str(e)

def process_uploaded_images(uploaded_files):
    """
    Verarbeitet eine Liste von Upload-Dateien.
    Gibt eine Liste von Dictionaries mit den Ergebnissen zurück.
    """
    results = []
    for uploaded in uploaded_files:
        filename = uploaded.name
        partei = find_partei_by_filename(filename)
        if not partei:
            results.append({
                'filename': filename,
                'partei_name': '– nicht gefunden –',
                'status': 'Fehler: Keine passende Partei',
                'target_path': ''
            })
            continue

        success, target_path, error = save_uploaded_image(uploaded, partei)
        if success:
            results.append({
                'filename': filename,
                'partei_name': partei.partei_name,
                'status': 'hochgeladen',
                'target_path': target_path
            })
        else:
            results.append({
                'filename': filename,
                'partei_name': partei.partei_name,
                'status': f'übersprungen ({error})',
                'target_path': target_path if target_path else ''
            })
    return results
