# lz_c_1: Hilfsfunktionen für den Bulk-Image-Import mit automatischer Erkennung
import os
import re
from django.conf import settings
from .models import Partei, Wahl

# -------------------------------------------------------------
# Hilfsfunktionen für Namensbereinigung (analog zu R)
# -------------------------------------------------------------

def replace_umlaute(s):
    """Ersetzt Umlaute und ß durch ae, oe, ue, ss."""
    umlaut_map = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'ß': 'ss'
    }
    for k, v in umlaut_map.items():
        s = s.replace(k, v)
    return s

def clean_partei_name(name):
    """
    Bereinigt den Parteiennamen analog zur R-Funktion clear_image_name.
    - Leerzeichen → _
    - Kleinbuchstaben
    - Entfernt Kommas, /, Punkte vor Unterstrichen
    - Ersetzt ' und - durch _
    - Entfernt dr._, med._, grünen, grüne
    - Ersetzt bündnis → b
    - Entfernt die_
    - Entfernt doppelte Unterstriche
    - Ersetzt Umlaute
    """
    s = name.replace(' ', '_')
    s = s.lower()
    s = s.replace(',', '')
    s = s.replace("'", '_')
    s = s.replace('-', '_')
    s = s.replace('/', '')
    s = re.sub(r'dr\._', '', s)
    s = re.sub(r'med\._', '', s)
    s = s.replace('grünen', '')
    s = s.replace('grüne', '')
    s = s.replace('bündnis', 'b')
    s = s.replace('die_', '')
    s = re.sub(r'\._', '_', s)
    while '__' in s:
        s = s.replace('__', '_')
    s = replace_umlaute(s)
    s = s.strip('_')
    return s

def extract_slug_and_name_from_filename(filename):
    """
    Extrahiert aus dem Dateinamen den Slug und den rohen Parteiennamen.
    Erwartet Format: <slug>__<bereinigter_parteiname>.<endung>
    Gibt Tuple (slug, raw_name) oder (None, None) bei Fehler.
    """
    base = os.path.basename(filename)
    # Dateiendung entfernen (nur erlaubte)
    for ext in ['.png', '.jpg', '.jpeg']:
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    else:
        return None, None

    if '__' not in base:
        return None, None
    slug, raw_name = base.split('__', 1)
    if not slug or not raw_name:
        return None, None
    return slug, raw_name

# -------------------------------------------------------------
# Hauptfunktion für die Verarbeitung
# -------------------------------------------------------------

def process_uploaded_images(uploaded_files):
    """
    Verarbeitet eine Liste von hochgeladenen Dateien.
    Extrahiert Slug und Parteienname aus dem Dateinamen,
    sucht die passende Partei (anhand der bereinigten Namen),
    setzt das partei_bild-Feld und speichert die Datei.
    Gibt eine Liste von Dictionaries mit den Ergebnissen zurück.
    """
    results = []

    for uploaded in uploaded_files:
        filename = uploaded.name
        slug, raw_name = extract_slug_and_name_from_filename(filename)

        if not slug or not raw_name:
            results.append({
                'filename': filename,
                'partei_name': '–',
                'status': 'Fehler',
                'message': 'Dateiname entspricht nicht dem Schema <slug>__<parteiname>.<endung>',
                'target_path': ''
            })
            continue

        # Wahl anhand Slug finden
        try:
            wahl = Wahl.objects.get(slug=slug)
        except Wahl.DoesNotExist:
            results.append({
                'filename': filename,
                'partei_name': '–',
                'status': 'Fehler',
                'message': f'Keine Wahl mit Slug "{slug}" gefunden',
                'target_path': ''
            })
            continue

        # Alle Parteien dieser Wahl durchgehen und bereinigten Namen vergleichen
        gefundene_partei = None
        for partei in Partei.objects.filter(wahl=wahl):
            cleaned = clean_partei_name(partei.partei_name)
            if cleaned == raw_name:
                gefundene_partei = partei
                break

        if not gefundene_partei:
            results.append({
                'filename': filename,
                'partei_name': raw_name,
                'status': 'Fehler',
                'message': f'Keine Partei in Wahl "{slug}" mit passendem Namen gefunden (bereinigt: {raw_name})',
                'target_path': ''
            })
            continue

        # Pfad im ImageField setzen: "partei_bild/<filename>"
        target_relative = f"partei_bild/{filename}"
        target_absolute = os.path.join(settings.MEDIA_ROOT, target_relative)

        # Zielverzeichnis anlegen
        os.makedirs(os.path.dirname(target_absolute), exist_ok=True)

        # Datei speichern (überschreibt vorhandene)
        try:
            with open(target_absolute, 'wb') as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)
        except Exception as e:
            results.append({
                'filename': filename,
                'partei_name': gefundene_partei.partei_name,
                'status': 'Fehler',
                'message': str(e),
                'target_path': target_relative
            })
            continue

        # Update des partei_bild-Feldes (setzt den Dateinamen, auch wenn vorher leer)
        gefundene_partei.partei_bild.name = target_relative
        gefundene_partei.save()

        results.append({
            'filename': filename,
            'partei_name': gefundene_partei.partei_name,
            'status': 'Erfolg',
            'message': '',
            'target_path': target_relative
        })

    return results
