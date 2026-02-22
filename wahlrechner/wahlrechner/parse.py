import copy
import os
import numpy
from django.http.response import Http404
from .models import These, Partei, Antwort

# lz_b_1: SCHLUESSEL bleibt unverändert, aber die Kodierung wird positionsbasiert
SCHLUESSEL = {
    "0": [None, None],  # These nicht beantwortet (Null)
    "1": ["a", False],  # Agree
    "2": ["d", False],  # Disagree
    "3": ["n", False],  # Neutral
    "5": ["a", True],   # Agree (Priorisiert)
    "6": ["d", True],   # Disagree (Priorisiert)
    "7": ["n", True],   # Neutral (Priorisiert)
    "9": ["s", False],  # These übersprungen (Skip)
}

def get_key_from_value(d, val):
    """Gibt Key für Wert val im Dictionary d zurück."""
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None

# lz_b_1: alle_thesen benötigt jetzt eine Wahl
def alle_thesen(wahl):
    """Gibt alle Thesen der übergebenen Wahl sortiert in einer Liste zurück."""
    return These.objects.filter(wahl=wahl).order_by("these_nr")

# lz_b_1: decode_zustand bekommt wahl und arbeitet positionsbasiert
def decode_zustand(zustand=0, wahl=None):
    """
    Dekodiert die Zustandsinformationen für eine bestimmte Wahl.
    Der Zustand ist eine Base-36-Zahl, deren Ziffern von rechts nach links
    den Thesen in der Reihenfolge ihrer these_nr entsprechen.
    """
    if wahl is None:
        raise ValueError("decode_zustand benötigt eine Wahl")

    # Kodiere den Zustand aus Base-36 in Base-10
    zustand = int(str(zustand).upper(), 36)

    # Lade alle Thesen der Wahl, sortiert nach these_nr
    thesen = list(alle_thesen(wahl))

    # Erstelle ein Dictionary mit allen Thesen, initial unbeantwortet
    opinions = {t: SCHLUESSEL.get("0").copy() for t in thesen}

    # Konvertiere zustand in eine Liste von Ziffern (von rechts nach links)
    # Beispiel: zustand = 1234 -> ziffern = [4,3,2,1] (die letzte Ziffer ist die Einerstelle)
    ziffern = [int(d) for d in str(zustand)[::-1]]

    for pos, status in enumerate(ziffern):
        # Falls ein Status 4 oder 8 ist, muss es sich um einen ungültigen Zustand handeln
        if status in [4, 8]:
            raise Http404
        # Nur wenn es eine These an dieser Position gibt
        if pos < len(thesen):
            t = thesen[pos]
            opinions[t] = SCHLUESSEL.get(str(status), SCHLUESSEL["0"]).copy()

    return opinions

# lz_b_1: encode_zustand benötigt wahl und arbeitet positionsbasiert
def encode_zustand(opinions, wahl):
    """
    Kodiert die Zustandsinformationen aus einem Opinions-Dictionary für eine Wahl.
    Gibt einen Zustand in Base-36 zurück.
    """
    thesen = list(alle_thesen(wahl))
    zustand = 0
    for pos, these in enumerate(thesen):
        status = get_key_from_value(SCHLUESSEL, opinions[these])
        if status is None:
            status = "0"
        zustand += int(status) * (10 ** pos)   # pos ist 0-basiert
    zustand = numpy.base_repr(zustand, 36)
    return zustand

# lz_b_1: generate_zustand benötigt wahl
def generate_zustand(opinions, these, opinion, wahl):
    """
    Gibt einen Zustand zurück, bei dem die Position bei these zu opinion geändert wurde.
    """
    opinions = copy.deepcopy(opinions)
    if not (prio := opinions[these][1]) or opinion == "s":
        prio = False
    opinions[these] = [opinion, prio]
    return encode_zustand(opinions, wahl)

# lz_b_1: thesen_index bleibt unverändert (arbeitet mit Liste)
def thesen_index(thesen, these_current):
    """Berechnet die Position der aktuellen These im Vergleich zu allen Thesen.
    Gibt ein Tuple zurück: (aktuelle_pos, max_pos)"""
    aktuelle_pos = (*thesen,).index(these_current) + 1
    max_pos = len(thesen)
    return aktuelle_pos, max_pos

# lz_b_1: diese Funktionen bleiben unverändert
def these_next(thesen, index):
    if index[0] < index[1]:
        return thesen[index[0]]
    else:
        return None

def these_prev(thesen, index):
    if index[0] > 1:
        return thesen[index[0] - 2]
    else:
        return None

# lz_b_1: update_opinions benötigt wahl
def update_opinions(opinions, get_dict, wahl):
    """
    Aktualisiert Opinion-Dictionary: Einträge ohne Positionierung werden als übersprungen markiert,
    Thesen mit einem passenden GET-Parameter werden als priorisiert markiert.
    """
    opinions = copy.deepcopy(opinions)
    for these in opinions.keys():
        if opinions[these] == [None, None]:
            opinions[these] = ["s", False]
        else:
            # Passe Priorisierung entsprechend der GET-Parameter an
            if get_dict.get(str(these.pk), False):
                opinions[these] = [opinions[these][0], True]
            else:
                opinions[these] = [opinions[these][0], False]
    return encode_zustand(opinions, wahl)

# lz_b_1: calc_result benötigt wahl
def calc_result(zustand, opinions, wahl):
    """Berechnet die Übereinstimmung zwischen Nutzer und Parteien für eine bestimmte Wahl."""
    caching_enabled = bool(int(os.getenv("WAHLRECHNER_CACHING", 0)))

    # Erstelle Cache-Dictionary falls nicht vorhanden
    if "cache" not in globals():
        global cache
        cache = dict()

    # Erhalte Ergebnis falls im Cache
    cache_key = f"{wahl.pk}_{zustand}"
    if cache_key in cache:
        results = cache.get(cache_key)
    else:
        results = []
        for partei in Partei.objects.filter(wahl=wahl):
            total_p = 0
            max_p = 0
            for antwort in Antwort.objects.filter(antwort_partei=partei):
                # Position des Nutzers
                opinion = opinions[antwort.antwort_these][0]
                prio = opinions[antwort.antwort_these][1]

                # Falls These nicht übersprungen
                if opinion != "s":
                    # Stimmt Position mit Antwort der Partei überein? (2 Punkte)
                    if opinion == antwort.antwort_position:
                        p = 2
                    # Teilweise Übereinstimmung, Position der Partei oder eigene Position neutral? (1 Punkt)
                    elif opinion == "n" or antwort.antwort_position == "n":
                        p = 1
                    # Keine Übereinstummung (0 Punkte)
                    else:
                        p = 0

                    # Ist These vom Nutzer priorisiert? (Doppelte Punkte)
                    if prio:
                        total_p += p * 2
                        max_p += 4
                    else:
                        total_p += p
                        max_p += 2

            if max_p == 0:
                percentage = 0
            else:
                percentage = round((total_p / max_p * 100), 1)

            results.append((partei, percentage))

        # Sortiere die Ergebnisse nach der prozentualen Übereinstimmung
        results.sort(key=lambda i: i[1], reverse=True)

        # Füge Ergebnis dem Cache hinzu
        if caching_enabled:
            cache[cache_key] = results

    return results

# lz_b_1: check_result benötigt wahl
def check_result(opinions, wahl):
    """Überprüft, ob ein Ergebnis aussagekräftig ist."""
    thesen = alle_thesen(wahl)
    skips = 0
    for these in thesen:
        if opinions[these][0] == "s":
            skips += 1
    if skips > thesen.count() * 0.7:
        return False
    else:
        return True

# lz_b_1: calc_antworten benötigt wahl
def calc_antworten(zustand, opinions, these, wahl):
    antworten = []
    for partei, _ in calc_result(zustand, opinions, wahl):
        try:
            antwort = Antwort.objects.get(antwort_these=these, antwort_partei=partei)
            antworten.append(antwort)
        except Antwort.DoesNotExist:
            pass
    return antworten

# lz_b_1: increase_result_count bleibt unverändert (optional könnte man pro Wahl zählen, erstmal global)
def increase_result_count():
    """Erhöht den Zähler result_count.txt um 1."""
    try:
        with open("wahlrechner/stats/result_count.txt", "r") as file:
            result_count = file.read()
        if result_count == "":
            result_count = 0
        else:
            result_count = int(result_count)
    except (FileNotFoundError, ValueError):
        result_count = 0

    result_count += 1

    if not os.path.exists("wahlrechner/stats"):
        os.mkdir("wahlrechner/stats")

    with open("wahlrechner/stats/result_count.txt", "w") as file:
        file.write(str(result_count))
