# lz_c_1: Hilfsfunktionen für den Bulk-Image-Import
# und Anpassunge lz_d_1
import os
from django.conf import settings
from .models import Partei

def extract_slug_from_filename(filename):
    """Extrahiert den Slug aus dem Dateinamen (vor dem ersten '__')."""
    base = os.path.basename(filename)
    if '__' not in base:
        return None
    slug, _ = base.split('__', 1)
    return slug if slug else None

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

    if os.path.exists(target_absolute):
        return False, target_relative, "Datei existiert bereits"

    os.makedirs(os.path.dirname(target_absolute), exist_ok=True)

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
        # Prüfe, ob der Dateiname dem Schema entspricht (optional)
        slug = extract_slug_from_filename(filename)
        if not slug:
            # Kein Fehler, aber für die Tabelle wird später 'unbekannt' angezeigt
            pass

        partei = find_partei_by_filename(filename)
        if not partei:
            results.append({
                'filename': filename,
                'partei_name': '– nicht gefunden –',
                'status': 'Fehler',
                'message': 'Keine Partei mit diesem Dateinamen gefunden',
                'target_path': '',
                'slug': slug or 'unbekannt'
            })
            continue

        success, target_path, error = save_uploaded_image(uploaded, partei)
        if success:
            results.append({
                'filename': filename,
                'partei_name': partei.partei_name,
                'status': 'Erfolg',
                'message': '',
                'target_path': target_path,
                'slug': slug or partei.wahl.slug  # Fallback auf Wahl-Slug der Partei
            })
        else:
            results.append({
                'filename': filename,
                'partei_name': partei.partei_name,
                'status': 'Fehler',
                'message': error,
                'target_path': target_path if target_path else '',
                'slug': slug or partei.wahl.slug
            })
    return results
