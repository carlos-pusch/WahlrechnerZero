from django.http.response import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from .models import Wahl # lz_b_1
from .parse import *

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
    context = {"thesen": thesen, "opinions": opinions, "wahl": wahl}
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

    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)
    context = {
        "opinions": opinions,
        "thesen": thesen,
        "zustand_current": zustand,
        "result": calc_result(zustand, opinions, wahl),
        "aussagekraeftig": check_result(opinions, wahl),
        "wahl": wahl,
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
