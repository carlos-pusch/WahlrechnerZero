from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Antwort, Partei, These, Wahl, Wartungszustand, BulkImageImport, TeamInfo, PointsBulkImport, OGBildBulkImport # lz_b_1 # lz_c_1 # lz_d_1 # lz_g_1
from django.shortcuts import redirect # lz_c_1

class WahlResource(resources.ModelResource):
    class Meta:
        model = Wahl

# lz_b_1: Admin für Wahl
@admin.register(Wahl)
class WahlAdmin(ImportExportModelAdmin):
    list_display = ['slug', 'titel', 'wahltypus', 'ist_aktiv','theme', 'og_image']
    list_editable = ['ist_aktiv', 'theme']
    list_display_links = ['slug'] # explizit, damit der Link erhalten bleibt
    list_filter = ['ist_aktiv', 'theme', 'titel']
    ordering = ["titel"]
    search_fields = ['slug', 'titel', 'wahltypus']
    prepopulated_fields = {'slug': ('titel',)}

class AntwortResource(resources.ModelResource):
    class Meta:
        model = Antwort

@admin.register(Antwort)
class AntwortAdmin(ImportExportModelAdmin):
    list_display = ["wahl", "antwort_partei", "antwort_these", "antwort_position"]
    list_display_links = ["antwort_partei", "antwort_these"]
    search_fields = [
        "antwort_these__these_text",
        "antwort_these__these_keyword",
        "antwort_these__these_explainer",
        "antwort_partei__partei_name",
        "wahl__titel", "wahl__slug"
    ]
    ordering = ["wahl", "antwort_partei", "antwort_these"]
    list_filter = ["antwort_position"]
    autocomplete_fields = ["wahl", "antwort_these", "antwort_partei"]
    resource_class = AntwortResource


class AntwortInLine(admin.TabularInline):
    model = Antwort
    extra = 1

class TheseResource(resources.ModelResource):
    class Meta:
        model = These

@admin.register(These)
class TheseAdmin(ImportExportModelAdmin):
    list_display = ["wahl", "these_nr", "these_keyword", "these_text", "these_explainer", "is_these"]   # lz_b_1: wahl ergänzt # lz_h_1
    list_display_links = ["these_keyword"]
    ordering = ["wahl", "these_nr", "these_keyword"]
    search_fields = ["these_keyword", "these_text", "these_explainer", "wahl__titel", "wahl__slug"]
    list_filter = ["is_these", "these_keyword"]
    ordering = ["wahl", "these_keyword", "these_explainer"]
    autocomplete_fields = ["wahl"]
    inlines = [AntwortInLine]
    resource_class = TheseResource

class ParteiResource(resources.ModelResource):
    class Meta:
        model = Partei

@admin.register(Partei)
class ParteiAdmin(ImportExportModelAdmin):
    list_display = ["wahl", "partei_name", "partei_farbe", "partei_gradient_css", "partei_bild"]   # lz_b_1: wahl ergänzt
    list_editable = ['partei_farbe', "partei_gradient_css", 'partei_bild']
    search_fields = ["partei_name", "wahl__titel", "wahl__slug", "partei_farbe"]
    list_filter = ["wahl"]   # lz_b_1: Filter nach Wahl
    ordering = ["wahl", "partei_name", "partei_farbe"]
    autocomplete_fields = ["wahl"]
    resource_class = ParteiResource

# lz_b_1: Admin für globale Einstellungen
@admin.register(Wartungszustand)
class WartungszustandAdmin(admin.ModelAdmin):
    list_display = ["__str__",'wartungsmodus', 'wartungsmeldung']
    list_editable = ['wartungsmodus', 'wartungsmeldung']

# lz_c_1: Admin für den Bulk-Image-Upload
@admin.register(BulkImageImport)
class BulkImageImportAdmin(admin.ModelAdmin):
    """
    Erzeugt einen Menüpunkt "06. Bildimporte" im Admin.
    Der Klick leitet auf die Bulk-Upload-View weiter.
    """
    def changelist_view(self, request, extra_context=None):
        # Umleitung auf die eigentliche Bulk-Upload-URL
        return redirect('bulk_upload')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# lz_d_1: Resource und Admin für TeamInfo
class TeamInfoResource(resources.ModelResource):
    class Meta:
        model = TeamInfo

@admin.register(TeamInfo)
class TeamInfoAdmin(ImportExportModelAdmin):
    resource_class = TeamInfoResource
    list_display = ['wahl', 'text', 'aktiv']
    list_filter = ['wahl']
    list_editable = ['text', 'aktiv']
    search_fields = ['wahl__titel', 'text']
    autocomplete_fields = ['wahl']
    ordering = ["wahl"]

    def text_preview(self, obj):
        """Zeigt einen kurzen Ausschnitt des Textes in der Listenansicht an."""
        return obj.text[:100] + '…' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text (Auszug)'

# lz_d_1: Admin für den Punkte-Bulkimport
@admin.register(PointsBulkImport)
class PointsBulkImportAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('points_bulk_upload')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# lz_f_1: Admin für OG‑Bilder‑Bulkimport
@admin.register(OGBildBulkImport)
class OGBildBulkImportAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('og_bild_bulk_upload')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
