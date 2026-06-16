import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from wahlrechner.views import bulk_upload # lz_c_1: Bulk-Upload-View importieren

# lz_b_1: Die feste URL_PREFIX wird entfernt, stattdessen dynamischer Slug

urlpatterns = [
    path('admin/bulk-upload/', bulk_upload, name='bulk_upload'),
    path('admin/', admin.site.urls),
    path('<slug:wahl_slug>/', include('wahlrechner.tenant_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Wahlrechner Admin"
admin.site.site_title = "Wahlrechner Admin"
admin.site.index_title = "Konfiguration"

handler404 = "wahlrechner.views.handler404"
handler500 = "wahlrechner.views.handler500"
