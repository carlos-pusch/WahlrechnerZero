from django.shortcuts import render
from django.urls import resolve
from .models import Wahl, GlobalSettings

# lz_b_1: Middleware für globalen Wartungsmodus
class MaintenanceModeMiddleware:
    """
    Zeigt bei aktivem Wartungsmodus für alle tenant-spezifischen URLs
    (beginnend mit /<slug>) eine Wartungsseite an. Admin-Bereich und
    statische/Medien-Pfade sind ausgenommen.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin-Pfad immer zulassen
        if request.path.startswith('/admin'):
            return self.get_response(request)

        # Prüfen, ob es sich um eine tenant-URL handelt (erstes Pfadsegment)
        path_parts = request.path.strip('/').split('/')
        if path_parts and path_parts[0] not in ['static', 'media']:
            # Versuche, den Slug als Wahl zu laden
            try:
                wahl = Wahl.objects.get(slug=path_parts[0])
                request.wahl = wahl  # für spätere Views verfügbar machen

                # Wartungsmodus prüfen
                settings = GlobalSettings.objects.first()
                if settings and settings.wartungsmodus:
                    # Wartungsseite rendern – Kontext mit Wahl für Theme und Titel
                    return render(request, 'wahlrechner/maintenance.html', {
                        'wahl': wahl,
                        'wartungsmeldung': settings.wartungsmeldung
                    })
            except Wahl.DoesNotExist:
                # Keine gültige Wahl – normal weiter (führt später zu 404)
                pass

        # Für alle anderen Fälle: normal fortfahren
        return self.get_response(request)
