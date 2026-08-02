# lz_f_1: Neue Datei für Bulk-Import von OG-Bildern (PNG/JPG)
import os
from django.conf import settings
from .bulk_points_import import extract_slug_from_filename   # 1:1 übernommen
from .models import Wahl

def process_uploaded_og_images(uploaded_files):
    """
    Verarbeitet eine Liste von hochgeladenen OG‑Bildern.
    Jede Datei wird als og_image der zugehörigen Wahl gespeichert.
    Der Dateiname muss das Schema <slug>__<beliebig>.png/.jpg haben.
    """
    results = []
    og_base = os.path.join(settings.MEDIA_ROOT, 'og_images')
    os.makedirs(og_base, exist_ok=True)

    for f in uploaded_files:
        filename = f.name
        slug = extract_slug_from_filename(filename)
        if not slug:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': 'Kein gültiger Slug im Dateinamen gefunden (Format: <slug>__<rest>.png/.jpg)'
            })
            continue

        # Wahl finden
        try:
            wahl = Wahl.objects.get(slug=slug)
        except Wahl.DoesNotExist:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': f'Keine Wahl mit Slug "{slug}" gefunden'
            })
            continue

        # Datei in media/og_images/ speichern (der Pfad muss dem upload_to in models.py entsprechen)
        target_path = os.path.join(og_base, filename)

        try:
            with open(target_path, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

            # Wahl‑Feld og_image auf den relativen Pfad setzen und speichern
            # Der Pfad innerhalb von MEDIA_ROOT muss 'og_images/<filename>' lauten.
            wahl.og_image.name = f'og_images/{filename}'
            wahl.save()

            results.append({
                'filename': filename,
                'wahl_slug': slug,
                'wahl_titel': wahl.titel,
                'status': 'Erfolg',
                'target_path': f'og_images/{filename}'
            })
        except Exception as e:
            results.append({
                'filename': filename,
                'status': 'Fehler',
                'message': str(e)
            })

    return results
