import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from wahlrechner.views import bulk_upload, image_delete_file, image_delete_all, download_parteien_csv, points_bulk_upload, points_delete_file, points_bulk_delete_files, og_bild_bulk_upload, og_bild_delete_file   # lz_c_1 # lz_d_1

# lz_b_1: Die feste URL_PREFIX wird entfernt, stattdessen dynamischer Slug

urlpatterns = [
    path('admin/bulk-upload/', bulk_upload, name='bulk_upload'),
    path('admin/bulk-upload/delete/<path:filename>/', image_delete_file, name='image_delete_file'),
    path('admin/bulk-upload/delete-all/', image_delete_all, name='image_delete_all'),
    path('admin/bulk-upload/download-csv/', download_parteien_csv, name='download_parteien_csv'),
    path('admin/og-bild-bulk-upload/', og_bild_bulk_upload, name='og_bild_bulk_upload'), # lz_f_1
    path('admin/og-bild-delete/<str:filename>/', og_bild_delete_file, name='og_bild_delete_file'), # lz_f_1
    path('admin/points-bulk-upload/', points_bulk_upload, name='points_bulk_upload'),  # lz_d_1
    path('admin/points-bulk-upload/delete/<slug:slug>/<path:filename>/', points_delete_file, name='points_delete_file'),  # lz_d_1
    path('admin/bulk-upload-points/delete-multiple/', points_bulk_delete_files, name='points_bulk_delete_files'),
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
