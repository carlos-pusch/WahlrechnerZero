from django.shortcuts import render
from django.urls import reverse
from .models import GlobalSettings, Wahl

# lz_b_2: Middleware für Wartungsmodus
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pfade, die auch im Wartungsmodus erreichbar sein sollen
        allowed_paths = [
            reverse('admin:index'),  # Admin-Index
            '/admin/',                # gesamter Admin-Bereich
            '/static/',
            '/media/',
        ]

        # Prüfen, ob Wartungsmodus aktiv
        if GlobalSettings.get_settings().wartungsmodus:
            path = request.path_info
            if not any(path.startswith(allowed) for allowed in allowed_paths):
                # Dummy-Wahl für das Base-Template
                dummy_wahl = Wahl(slug='', titel='Wartungsarbeiten', theme='theme_localzero')
                return render(
                    request,
                    'wahlrechner/maintenance.html',
                    {'wahl': dummy_wahl},
                    status=503
                )

        return self.get_response(request)
