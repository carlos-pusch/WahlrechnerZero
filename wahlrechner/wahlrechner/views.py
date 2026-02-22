from django.http.response import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from .models import Wahl   # lz_b_1: Wahl importieren
from .parse import *

# lz_b_1: Alle Views bekommen einen wahl_slug Parameter und laden die Wahl
def start(request, wahl_slug):
    wahl = get_object_or_404(Wahl, slug=wahl_slug, ist_aktiv=True)
    thesen = alle_thesen(wahl)
    opinions = decode_zustand(0, wahl)  # Startzustand (alles 0)
    context = {
        "thesen": thesen,
        "opinions": opinions,
        "wahl": wahl,          # optional im Template
    }
    return render(request, "wahlrechner/start.html", context)

def these(request, wahl_slug, these_pk, zustand):
    wahl = get_object_or_404(Wahl, slug=wahl_slug, ist_aktiv=True)
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

def confirm(request, wahl_slug, zustand):
    wahl = get_object_or_404(Wahl, slug=wahl_slug, ist_aktiv=True)
    opinions = decode_zustand(zustand, wahl)
    thesen = alle_thesen(wahl)
    context = {
        "opinions": opinions,
        "thesen": thesen,
        "zustand_current": zustand,
        "wahl": wahl,
    }
    return render(request, "wahlrechner/confirm.html", context)

def confirm_submit(request, wahl_slug, zustand):
    wahl = get_object_or_404(Wahl, slug=wahl_slug, ist_aktiv=True)
    opinions = decode_zustand(zustand, wahl)
    zustand = update_opinions(opinions, request.GET, wahl)
    return redirect("result", wahl_slug=wahl_slug, zustand=zustand)

def result(request, wahl_slug, zustand):
    wahl = get_object_or_404(Wahl, slug=wahl_slug, ist_aktiv=True)
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

def reason(request, wahl_slug, these_pk, zustand):
    wahl = get_object_or_404(Wahl, slug=wahl_slug, ist_aktiv=True)
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

# lz_b_1: Handler bleiben unverändert (keine wahl_slug nötig)
def handler404(request, exception=""):
    return HttpResponseNotFound(render_to_string("error/404.html"))

def test404(request):
    return render(request, template_name="error/404.html")

def handler500(request):
    return HttpResponseServerError(render_to_string("error/500.html"))

def test500(request):
    return render(request, template_name="error/500.html")
