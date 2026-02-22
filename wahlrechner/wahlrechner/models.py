from colorfield.fields import ColorField
from django.db import models

# lz_b_1: Neues Modell für Mandanten (Wahlen)
class Wahl(models.Model):
    """
    Repräsentiert eine einzelne Wahl / einen Mandanten.
    Jede Wahl hat einen eigenen Slug für die URL, einen Titel,
    ein Theme und einen Aktiv-Status.
    """
    slug = models.SlugField(
        "URL-Kennung",
        max_length=50,
        unique=True,
        help_text="Eindeutige Kurzbezeichnung für die URL (z.B. 'bundestagswahl-2025')"
    )
    titel = models.CharField(
        "Titel der Wahl",
        max_length=200,
        help_text="Angezeigter Name im Wahlrechner"
    )
    theme = models.CharField(
        "Theme",
        max_length=50,
        default="theme_localzero",
        help_text="Name des zu verwendenden Themes (Ordner im themes-Verzeichnis)"
    )
    ist_aktiv = models.BooleanField(
        "Aktiv",
        default=True,
        help_text="Nur aktive Wahlen sind über die URL erreichbar"
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    geaendert_am = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wahl"
        verbose_name_plural = "Wahlen"

    def __str__(self):
        return self.titel


class These(models.Model):
    # lz_b_1: Fremdschlüssel zur Wahl hinzugefügt
    wahl = models.ForeignKey(
        Wahl,
        on_delete=models.CASCADE,
        verbose_name="Wahl",
        related_name="thesen"
    )

    these_keyword_help = """<i>Maximal 40 Zeichen</i><br>
    Ein kurzes Schlagwort, um die These zu beschreiben. Wird in der
    Seitenleiste des Wahlrechners angezeigt.<br>
    <b>Beispiel:</b> Klimanotstand"""
    these_keyword = models.CharField(
        "Schlagwort", help_text=these_keyword_help, max_length=40, blank=True
    )

    these_text_help = """<i>Maximal 400 Zeichen</i><br>
    Der vollständige Text der These.<br>
    <b>Beispiel:</b> Die Stadt XYZ sollte den Klimanotstand ausrufen."""
    these_text = models.TextField(
        "Vollständige These", help_text=these_text_help, max_length=400, blank=True
    )

    # lz_a_1: Neues Feld für Erklärungssätze
    these_explainer_help = """<i>Optionale Hintergrundinformation</i><br>
    Erklärungssätze zur These, die als zusätzliche Information angezeigt werden."""
    these_explainer = models.TextField(
        "Hintergrundinformation",
        help_text=these_explainer_help,
        max_length=1500,
        blank=True,
        null=True,
        default=None
    )

    these_nr_help = """Die Thesen-Nummer gibt Auskunft über die Reihenfolge, in der alle Thesen
    angezeigt werden. Dabei wird als erstes die These mit der niedrigsten Thesen-Nummer angezeigt,
    danach die These mit der jeweils nächst größeren Thesen-Nummer, usw. Die Thesen-Nummer lässt
    sich also als Priorität für die angezeigte Reihenfolge verstehen, und kann auch eine krumme
    Zahl sein.<br>
    <b>Beispiel:</b> Die These, die zuerst angezeigt werden soll, hat die Nummer 1. Die zweite These
    die Nummer 2, usw."""
    these_nr = models.FloatField("Thesen-Nummer", help_text=these_nr_help)

    class Meta:
        verbose_name = "These"
        verbose_name_plural = "Thesen"
        # lz_b_1: Eindeutigkeit pro Wahl erzwingen
        unique_together = [['wahl', 'these_nr']]

    def __str__(self):
        return f"{self.wahl.slug} - {self.these_keyword}"


class Partei(models.Model):
    # lz_b_1: Fremdschlüssel zur Wahl hinzugefügt
    wahl = models.ForeignKey(
        Wahl,
        on_delete=models.CASCADE,
        verbose_name="Wahl",
        related_name="parteien"
    )

    partei_name_help = """<i>Maximal 50 Zeichen</i><br>
    Gib den Namen der Partei an, der für den Benutzer angezeigt werden soll."""
    partei_name = models.CharField("Name", help_text=partei_name_help, max_length=50)

    partei_beschreibung_help = """<i>Maximal 1500 Zeichen</i><br>
    Beschreibung für die Partei, wird auf der Ergebnis-Seite angezeigt."""
    partei_beschreibung = models.TextField(
        "Beschreibung", help_text=partei_beschreibung_help, max_length=1500, blank=True
    )

    partei_bild_beschreibung = (
        """Logo oder Foto, das auf der Ergebnis-Seite angezeigt werden soll."""
    )
    partei_bild = models.ImageField(
        "Bild",
        upload_to="partei_bild",
        help_text=partei_bild_beschreibung,
        blank=True,
        null=True,
        default=None,
    )

    partei_farbe_beschreibung = """Akzentfarbe der Partei, die als Streifen neben dem Ergebnis angezeigt wird."""
    partei_farbe = ColorField(
        "Akzentfarbe",
        null=True,
        blank=True,
        help_text=partei_farbe_beschreibung,
        default=None,
    )

    class Meta:
        verbose_name = "Partei"
        verbose_name_plural = "Parteien"
        # lz_b_1: Name pro Wahl eindeutig (optional)
        unique_together = [['wahl', 'partei_name']]

    def __str__(self):
        return f"{self.wahl.slug} - {self.partei_name}"


class Antwort(models.Model):
    # lz_b_1: Fremdschlüssel zur Wahl hinzugefügt (kann über These oder Partei abgeleitet werden, aber für einfachere Abfragen direkt)
    wahl = models.ForeignKey(
        Wahl,
        on_delete=models.CASCADE,
        verbose_name="Wahl",
        editable=False,  # wird automatisch gesetzt
        null=True        # für bestehende Daten, wird aber durch Signal gesetzt
    )

    antwort_these = models.ForeignKey(
        These, on_delete=models.CASCADE, verbose_name="These"
    )
    antwort_partei = models.ForeignKey(
        Partei, on_delete=models.CASCADE, verbose_name="Partei"
    )

    antwort_position_choices = [
        ("a", "stimmt zu"),
        ("d", "stimmt nicht zu"),
        ("n", "neutral"),
    ]
    antwort_position_help = (
        """Wähle aus, wie sich die Partei zu der ausgewählten These positioniert."""
    )
    antwort_position = models.CharField(
        "Position zur These",
        choices=antwort_position_choices,
        help_text=antwort_position_help,
        max_length=1,
    )

    antwort_text_help = """<i>Maximal 1500 Zeichen</i><br>
    Vollständige Antwort/Begründung der Partei zu ihrer Position."""
    antwort_text = models.TextField(
        "Antwort", help_text=antwort_text_help, max_length=1500, blank=True
    )

    class Meta:
        verbose_name = "Antwort"
        verbose_name_plural = "Antworten"
        unique_together = [['antwort_these', 'antwort_partei']]

    def __str__(self):
        return f"{self.antwort_these.these_keyword} - {self.antwort_partei.partei_name}"

    # lz_b_1: Automatisches Setzen der wahl beim Speichern
    def save(self, *args, **kwargs):
        if not self.wahl_id:
            self.wahl = self.antwort_these.wahl
        super().save(*args, **kwargs)
