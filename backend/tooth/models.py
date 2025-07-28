# Create your models here.
from django.db import models
import uuid
from django.conf import settings


class Tooth(models.Model):
    """
    Represents a universal tooth identified by standard numbering systems.
    This table resides in the public schema and is shared across all tenants.
    """
    class Arch(models.TextChoices):
        MAXILLARY = 'MAX', 'Maxillary (Upper)'
        MANDIBULAR = 'MAN', 'Mandibular (Lower)'

    class Quadrant(models.TextChoices):
        UPPER_RIGHT = 'UR', 'Upper Right'
        UPPER_LEFT = 'UL', 'Upper Left'
        LOWER_RIGHT = 'LR', 'Lower Right'
        LOWER_LEFT = 'LL', 'Lower Left'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    universal_number = models.CharField(
        max_length=3,
        unique=True,
        null=True,
        blank=True,
        help_text="Universal Numbering System (e.g., 1-32 for permanent, A-T for primary)"
    )
    fdi_number = models.CharField(
        max_length=2,
        unique=True,
        help_text="FDI World Dental Federation notation (e.g., 11-48 for permanent, 51-85 for primary)"
    )
    palmer_notation = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        help_text="Palmer notation symbol (e.g., ┘1, └8)"
    )
    # REMOVED generic name field
    # name = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     help_text="Common name (e.g., Upper Right Third Molar)"
    # )
    name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Common name in English"
    )
    name_fr = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Common name in French"
    )
    arch = models.CharField(
        max_length=3,
        choices=Arch.choices,
        null=True,
        blank=True
    )
    quadrant = models.CharField(
        max_length=2,
        choices=Quadrant.choices,
        null=True,
        blank=True
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Is this a primary (deciduous/baby) tooth?"
    )

    class Meta:
        verbose_name = "Tooth"
        verbose_name_plural = "Teeth"
        ordering = ['fdi_number'] # Order predictably

    def __str__(self):
        parts = [f"Tooth {self.fdi_number}"]
        if self.universal_number:
            parts.append(f"(Univ: {self.universal_number})")
        if self.name_en:
             parts.append(f"- {self.name_en}")
        return " ".join(parts)
    
    def get_name(self, lang_code):
        if lang_code.lower() in settings.SUPPORTED_LANGS:
            attr_name = f"name_{lang_code.lower()}"
            return getattr(self, attr_name)
        return self.name_en

    # You might want a script or data migration to populate this table
    # with the standard 32 permanent teeth and 20 primary teeth.
    
    
