from django.http.response import HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from .models import Wahl # lz_b_1
from .parse import *
from django.urls import reverse # lz_d_1
import os
from django.conf import settings
from .bulk_points_import import process_uploaded_points_files
from django.contrib import messages
import time

# lz_b_1: Hilfsfunktion für Dummy-Wahl bei 404
def _get_dummy_wahl():
    """Erzeugt ein temporäres Wahl-Objekt für die 404-Seite."""
    return Wahl(slug='', titel='Seite nicht gefunden', theme='theme_localzero')

# lz_b_1: Startseite einer Wahl
def start(request, wahl_slug):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    thesen = alle_thesen(wahl)
    opinions = decode_zustand(0, wahl)
    context = { # lz_d_1
        "thesen": thesen,
        "opinions": opinions,
        "wahl": wahl,
        "share_url": request.build_absolute_uri(reverse('start', args=[wahl.slug])),
        "share_title": wahl.titel,
        "share_dialog_title": "Kennst du schon unseren Wahlcheck?\nErzähle anderen davon!",
    }
    return render(request, "wahlrechner/start.html", context)

# lz_b_1: Detailseite einer These
def these(request, wahl_slug, these_pk, zustand):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    these_current = get_object_or_404(These, pk=these_pk, wahl=wahl)
    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)
    index = thesen_index(thesen, these_current)

    context = {
        "opinions": opinions,
        "index": index,
        "thesen": thesen,
        "these_current": these_current,
        "these_next": these_next(thesen, index),
        "these_prev": these_prev(thesen, index),
        "zustand_current": zustand,
        "zustand_agree": generate_zustand(opinions, these_current, "a", wahl),
        "zustand_disagree": generate_zustand(opinions, these_current, "d", wahl),
        "zustand_neutral": generate_zustand(opinions, these_current, "n", wahl),
        "zustand_skip": generate_zustand(opinions, these_current, "s", wahl),
        "wahl": wahl,
    }
    return render(request, "wahlrechner/these.html", context)

# lz_b_1: Bestätigungsseite (Gewichtung)
def confirm(request, wahl_slug, zustand):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)
    context = {
        "opinions": opinions,
        "thesen": thesen,
        "zustand_current": zustand,
        "wahl": wahl,
    }
    return render(request, "wahlrechner/confirm.html", context)

# lz_b_1: Bestätigung absenden (Prioritäten setzen)
def confirm_submit(request, wahl_slug, zustand):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    opinions = decode_zustand(zustand, wahl)
    zustand = update_opinions(opinions, request.GET, wahl)
    return redirect("result", wahl_slug=wahl_slug, zustand=zustand)

# lz_b_1: Ergebnis-Seite
def result(request, wahl_slug, zustand):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    points_parlament_url = None
    points_these_url = None

    points_dir = os.path.join(settings.MEDIA_ROOT, 'punkte_grafiken', wahl.slug)
    if os.path.isdir(points_dir):
        base_parlament = f"{wahl.slug}__Gesamtpunkte_nach_Parlamentswahl__-1_1"
        base_these = f"{wahl.slug}__Punkte_nach_These_und_Parlamentswahl__-1_1"
        
        if os.path.exists(os.path.join(points_dir, f"{base_parlament}.html")):
            points_parlament_url = settings.MEDIA_URL + f"punkte_grafiken/{wahl.slug}/{base_parlament}.html"
        elif os.path.exists(os.path.join(points_dir, f"{base_parlament}.png")):
            points_parlament_url = settings.MEDIA_URL + f"punkte_grafiken/{wahl.slug}/{base_parlament}.png"
        
        if os.path.exists(os.path.join(points_dir, f"{base_these}.html")):
            points_these_url = settings.MEDIA_URL + f"punkte_grafiken/{wahl.slug}/{base_these}.html"
        elif os.path.exists(os.path.join(points_dir, f"{base_these}.png")):
            points_these_url = settings.MEDIA_URL + f"punkte_grafiken/{wahl.slug}/{base_these}.png"
    
    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)
    context = { # lz_d_1
        "opinions": opinions,
        "thesen": thesen,
        "zustand_current": zustand,
        "result": calc_result(zustand, opinions, wahl),
        "aussagekraeftig": check_result(opinions, wahl),
        "wahl": wahl,
        "share_url": request.build_absolute_uri(reverse('start', args=[wahl.slug])),
        "share_title": wahl.titel,
        "share_dialog_title": "Ich habe unseren Wahlcheck ausgefüllt!\nDu auch?",
        "points_parlament_url": points_parlament_url,
        "points_these_url": points_these_url,
    }
    increase_result_count()

    return render(request, "wahlrechner/result.html", context)

# lz_b_1: Begründungs-Seite
def reason(request, wahl_slug, these_pk, zustand):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    these_current = get_object_or_404(These, pk=these_pk, wahl=wahl)
    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)
    index = thesen_index(thesen, these_current)
    context = {
        "opinions": opinions,
        "index": index,
        "thesen": thesen,
        "these_current": these_current,
        "these_next": these_next(thesen, index),
        "these_prev": these_prev(thesen, index),
        "zustand_current": zustand,
        "antworten": calc_antworten(zustand, opinions, these_current, wahl),
        "wahl": wahl,
    }
    return render(request, "wahlrechner/reason.html", context)

# lz_b_1: Globale 404-Fehler (für andere Pfade, z.B. nicht existierende These)
def handler404(request, exception=""):
    return HttpResponseNotFound(render_to_string("error/404.html"))

def test404(request):
    return render(request, template_name="error/404.html")

def handler500(request):
    return HttpResponseServerError(render_to_string("error/500.html"))

def test500(request):
    return render(request, template_name="error/500.html")

# lz_c_1: Bulk-Bildupload-View
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse
from .bulk_image_import import process_uploaded_images
import csv
import io

@staff_member_required
def bulk_upload(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        uploaded_files = request.FILES.getlist('images')
        results = process_uploaded_images(uploaded_files)

        success_count = sum(1 for r in results if r['status'] == 'Erfolg')
        error_count = len(results) - success_count

        if success_count:
            messages.success(request, f"{success_count} Bild(er) erfolgreich hochgeladen.")
        if error_count:
            messages.warning(request, f"{error_count} Bild(er) konnten nicht hochgeladen werden. Details siehe unten.")

        request.session['upload_results'] = results
        return redirect('bulk_upload')

    # --- GET: Liste vorhandener Bilder anzeigen ---
    bilder_ordner = os.path.join(settings.MEDIA_ROOT, 'partei_bild')
    files_data = []
    if os.path.isdir(bilder_ordner):
        for filename in os.listdir(bilder_ordner):
            # Nur Bilddateien berücksichtigen
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(bilder_ordner, filename)
                # Slug aus Dateinamen extrahieren
                slug = 'unbekannt'
                if '__' in filename:
                    slug, _ = filename.split('__', 1)
                files_data.append({
                    'slug': slug,
                    'filename': filename,
                    'url': settings.MEDIA_URL + f"partei_bild/{filename}",
                    'size': os.path.getsize(filepath),
                    'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(filepath))),
                })
    # Sortierung nach Slug, dann Dateiname
    files_data.sort(key=lambda x: (x['slug'], x['filename']))

    # Detaillierte Ergebnisse aus Session holen
    upload_results = request.session.pop('upload_results', None)
    if upload_results:
        upload_results.sort(key=lambda x: 0 if x['status'] == 'Fehler' else 1)
        for result in upload_results:
            if result['status'] == 'Erfolg':
                messages.success(request, f"✅ {result['filename']} – hochgeladen nach {result.get('target_path', '')}")
            else:
                messages.error(request, f"❌ {result['filename']}: {result.get('message', 'Unbekannter Fehler')}")

    return render(request, 'admin/bulk_upload.html', {'files': files_data})

@staff_member_required
def image_delete_file(request, filename):
    """
    Löscht eine einzelne Partei-Bild-Datei.
    Nur PNG, JPG, JPEG sind erlaubt.
    """
    # Sicherheitsprüfung: nur erlaubte Endungen
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return HttpResponseBadRequest("Ungültiger Dateiname – nur PNG, JPG und JPEG sind erlaubt.")

    base_dir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'partei_bild'))
    filepath = os.path.join(base_dir, filename)
    abs_path = os.path.abspath(filepath)

    if not abs_path.startswith(base_dir):
        return HttpResponseBadRequest("Ungültiger Pfad.")

    if os.path.exists(abs_path):
        os.remove(abs_path)
        messages.success(request, f"Die Datei „{filename}“ wurde erfolgreich gelöscht.")
    else:
        messages.error(request, f"Die Datei „{filename}“ wurde nicht gefunden.")

    return redirect('bulk_upload')

@staff_member_required
def points_bulk_upload(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        uploaded_files = request.FILES.getlist('images')
        results = process_uploaded_points_files(uploaded_files)

        # Erfolgs- und Fehlerzahlen für eine kurze Zusammenfassung
        success_count = sum(1 for r in results if r['status'] == 'Erfolg')
        error_count = len(results) - success_count

        if success_count:
            messages.success(request, f"{success_count} Datei(en) erfolgreich hochgeladen.")
        if error_count:
            messages.warning(request, f"{error_count} Datei(en) konnten nicht hochgeladen werden. Details siehe unten.")

        # Detaillierte Ergebnisse in der Session speichern
        request.session['upload_results'] = results

        # Redirect auf die gleiche Seite (GET), damit die Tabelle aktualisiert wird
        return redirect('points_bulk_upload')

    # --- GET: Liste vorhandener Dateien anzeigen ---
    points_base = os.path.join(settings.MEDIA_ROOT, 'punkte_grafiken')
    files_data = []
    if os.path.isdir(points_base):
        for slug in os.listdir(points_base):
            dir_path = os.path.join(points_base, slug)
            if os.path.isdir(dir_path):
                for filename in os.listdir(dir_path):
                    if filename.lower().endswith(('.png', '.html')):
                        filepath = os.path.join(dir_path, filename)
                        files_data.append({
                            'slug': slug,
                            'filename': filename,
                            'url': settings.MEDIA_URL + f"punkte_grafiken/{slug}/{filename}",
                            'size': os.path.getsize(filepath),
                            'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(filepath))),
                        })
    files_data.sort(key=lambda x: (x['slug'], x['filename']))

    # Prüfen, ob es detaillierte Ergebnisse aus einem vorherigen Upload gibt
    upload_results = request.session.pop('upload_results', None)
    if upload_results:
        # Sortiere: Fehler zuerst (status == 'Fehler'), dann Erfolg
        upload_results.sort(key=lambda x: 0 if x['status'] == 'Fehler' else 1)
        for result in upload_results:
            if result['status'] == 'Erfolg':
                messages.success(request, f"✅ {result['filename']} – hochgeladen nach {result.get('target_path', '')}")
            else:
                messages.error(request, f"❌ {result['filename']}: {result.get('message', 'Unbekannter Fehler')}")

    return render(request, 'admin/bulk_upload_punkte.html', {'files': files_data})

@staff_member_required
def points_delete_file(request, slug, filename):
    """
    Löscht eine einzelne Punktegrafik-Datei.
    Nur PNG und HTML sind erlaubt.
    """
    # Sicherheitsprüfung: nur erlaubte Endungen
    if not filename.lower().endswith(('.png', '.html')):
        return HttpResponseBadRequest("Ungültiger Dateiname – nur PNG und HTML sind erlaubt.")

    # Absoluten Pfad berechnen und prüfen, ob er innerhalb des Punkte-Ordners liegt
    base_dir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'punkte_grafiken'))
    filepath = os.path.join(base_dir, slug, filename)
    abs_path = os.path.abspath(filepath)

    if not abs_path.startswith(base_dir):
        return HttpResponseBadRequest("Ungültiger Pfad.")

    if os.path.exists(abs_path):
        os.remove(abs_path)
        messages.success(request, f"Die Datei „{filename}“ wurde erfolgreich gelöscht.")
    else:
        messages.error(request, f"Die Datei „{filename}“ wurde nicht gefunden.")

    return redirect('points_bulk_upload')

# lz_f_1: Neue Vergleichsansicht
def compare(request, wahl_slug, zustand):
    try:
        wahl = Wahl.objects.get(slug=wahl_slug)
    except Wahl.DoesNotExist:
        dummy = _get_dummy_wahl()
        return render(request, "wahlrechner/error_404.html", {"wahl": dummy}, status=404)

    if not wahl.ist_aktiv:
        return render(request, "wahlrechner/inactive.html", {"wahl": wahl})

    # Lese die ausgewählten Partei-IDs aus GET-Parametern
    partei_ids_str = request.GET.get('parteien', '')
    partei_ids = []
    if partei_ids_str:
        try:
            partei_ids = [int(id) for id in partei_ids_str.split(',') if id.strip()]
        except ValueError:
            pass

    # Lade die Parteien und behalte die Reihenfolge aus der URL
    parteien = Partei.objects.filter(wahl=wahl, pk__in=partei_ids)
    parteien_dict = {p.pk: p for p in parteien}
    parteien_geordnet = [parteien_dict[id] for id in partei_ids if id in parteien_dict]

    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)

    # Sammle für jede These die User-Position und die Antworten der Parteien
    thesen_daten = []
    for these in thesen:
        user_position = opinions[these][0]  # 'a', 'd', 'n', 's' oder None
        partei_antworten = []
        for partei in parteien_geordnet:
            try:
                antwort = Antwort.objects.get(antwort_these=these, antwort_partei=partei)
                partei_antworten.append({
                    'partei': partei,
                    'position': antwort.antwort_position,
                    'text': antwort.antwort_text,
                })
            except Antwort.DoesNotExist:
                partei_antworten.append({
                    'partei': partei,
                    'position': None,
                    'text': None,
                })
        thesen_daten.append({
            'these': these,
            'user_position': user_position,
            'partei_antworten': partei_antworten,
        })

    context = {
        'wahl': wahl,
        'thesen_daten': thesen_daten,
        'zustand': zustand,
        'parteien': parteien_geordnet,
        'share_url': request.build_absolute_uri(reverse('start', args=[wahl.slug])),
        'share_title': wahl.titel,
        'share_dialog_title': "Vergleiche die Positionen im Wahlcheck!",
    }
    return render(request, "wahlrechner/compare.html", context)
