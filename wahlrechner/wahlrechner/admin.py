from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Antwort, Partei, These, Wahl   # lz_b_1: Wahl importiert

# lz_b_1: Admin für Wahl
@admin.register(Wahl)
class WahlAdmin(admin.ModelAdmin):
    list_display = ['slug', 'titel', 'theme', 'ist_aktiv', 'erstellt_am']
    list_filter = ['ist_aktiv', 'theme']
    search_fields = ['slug', 'titel']
    prepopulated_fields = {'slug': ('titel',)}


class AntwortResource(resources.ModelResource):
    class Meta:
        model = Antwort

@admin.register(Antwort)
class AntwortAdmin(ImportExportModelAdmin):
    list_display = ["antwort_partei", "antwort_these", "antwort_position"]
    list_display_links = ["antwort_partei", "antwort_these"]
    search_fields = [
        "antwort_these__these_text",
        "antwort_these__these_keyword",
        "antwort_these__these_explainer",
        "antwort_partei__partei_name",
    ]
    list_filter = ["antwort_partei", "wahl"]   # lz_b_1: Filter nach Wahl
    autocomplete_fields = ["antwort_these", "antwort_partei"]
    resource_class = AntwortResource


class AntwortInLine(admin.TabularInline):
    model = Antwort
    extra = 1


class TheseResource(resources.ModelResource):
    class Meta:
        model = These

@admin.register(These)
class TheseAdmin(ImportExportModelAdmin):
    list_display = ["wahl", "these_nr", "these_keyword", "these_text", "these_explainer"]   # lz_b_1: wahl ergänzt
    list_display_links = ["these_keyword"]
    ordering = ["wahl", "these_nr"]
    search_fields = ["these_keyword", "these_text", "these_explainer"]
    list_filter = ["wahl"]   # lz_b_1: Filter nach Wahl
    inlines = [AntwortInLine]
    resource_class = TheseResource

class ParteiResource(resources.ModelResource):
    class Meta:
        model = Partei

@admin.register(Partei)
class ParteiAdmin(ImportExportModelAdmin):
    list_display = ["wahl", "partei_name", "partei_farbe"]   # lz_b_1: wahl ergänzt
    search_fields = ["partei_name"]
    list_filter = ["wahl"]   # lz_b_1: Filter nach Wahl
    resource_class = ParteiResource
