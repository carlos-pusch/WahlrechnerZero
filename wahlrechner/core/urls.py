import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# lz_b_1: Die feste URL_PREFIX wird entfernt, stattdessen dynamischer Slug

urlpatterns = [
    # Admin bleibt global erreichbar (z.B. unter /admin)
    path('admin/', admin.site.urls),

    # lz_b_1: Alle wahlrechner-Pfade beginnen mit dem Slug der Wahl
    path('<slug:wahl_slug>/', include('wahlrechner.tenant_urls')),
]

# Statische und Medien-Dateien im Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Wahlrechner Admin"
admin.site.site_title = "Wahlrechner Admin"
admin.site.index_title = "Konfiguration"

handler404 = "wahlrechner.views.handler404"
handler500 = "wahlrechner.views.handler500"
