# lz_d_1: Neue Datei für Bulk-Import von Punktegrafiken (PNG/HTML)
import os
import re
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from .models import Wahl

ALLOWED_GRAPHIC_PREFIXES = [
    "Gesamtpunkte_nach_",
    "Punkte_nach_These_und_",
]

def extract_slug_from_filename(filename: str) -> str:
    """
    Extrahiert den Wahl-Slug aus dem Dateinamen.
    Erwartet Format: <slug>__<beliebiger_rest> (zwei Unterstriche als Trenner).
    Gibt den Slug zurück oder None, wenn nicht gefunden.
    """
    base = os.path.basename(filename)
    # Suche nach zwei Unterstrichen
    if '__' not in base:
        return None
    slug, _ = base.split('__', 1)
    return slug if slug else None

def process_uploaded_points_files(uploaded_files):
    """
    Verarbeitet eine Liste von hochgeladenen Dateien (PNG/HTML) für Punktegrafiken.
    Jede Datei wird in media/punkte_grafiken/<slug>/ abgelegt.
    Es wird geprüft:
      - Der Slug muss aus dem Dateinamen extrahierbar sein (vor dem ersten '__').
      - Der Teil nach dem ersten '__' (ohne Dateiendung) muss mit einem der
        erlaubten Präfixe beginnen (Gesamtpunkte_nach_ oder Punkte_nach_These_und_).
      - Die Wahl mit dem Slug muss in der Datenbank existieren.
    Gibt eine Liste von Dictionaries mit Statusinformationen zurück.
    """
    results = []
    points_base = os.path.join(settings.MEDIA_ROOT, 'punkte_grafiken')
    os.makedirs(points_base, exist_ok=True)

    for f in uploaded_files:
        filename = f.name
        slug = extract_slug_from_filename(filename)
        if not slug:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': 'Slug konnte nicht aus Dateinamen extrahiert werden (erwartet: <slug>__<typ>)'
            })
            continue

        # Dateiendung entfernen, um den reinen Namen zu erhalten
        base = os.path.basename(filename)
        name_without_ext = base
        for ext in ['.png', '.html']:
            if base.endswith(ext):
                name_without_ext = base[:-len(ext)]
                break

        # Prüfen, ob der Teil nach dem ersten '__' einem erlaubten Präfix entspricht
        if '__' not in name_without_ext:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': 'Dateiname enthält nicht das erwartete Trennzeichen "__" (nach dem Slug)'
            })
            continue

        _, typ_part = name_without_ext.split('__', 1)

        # Prüfen, ob der Typ mit einem der erlaubten Präfixe beginnt
        valid_prefix = any(typ_part.startswith(prefix) for prefix in ALLOWED_GRAPHIC_PREFIXES)
        if not valid_prefix:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': f'Ungültiger Bildtyp "{typ_part}". Erwartet wird ein Name, der mit "Gesamtpunkte_nach_" oder "Punkte_nach_These_und_" beginnt.'
            })
            continue

        # Prüfen, ob die Wahl existiert
        try:
            wahl = Wahl.objects.get(slug=slug)
        except Wahl.DoesNotExist:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': f'Keine Wahl mit Slug "{slug}" gefunden'
            })
            continue

        # Zielverzeichnis anlegen
        target_dir = os.path.join(points_base, slug)
        os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(target_dir, filename)

        # Datei speichern
        try:
            with open(target_path, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            results.append({
                'filename': filename,
                'wahl_slug': slug,
                'wahl_titel': wahl.titel,
                'status': 'Erfolg',
                'target_path': os.path.join('punkte_grafiken', slug, filename)
            })
        except Exception as e:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': str(e)
            })

    return results
