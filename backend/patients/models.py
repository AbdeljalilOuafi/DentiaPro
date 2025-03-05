from django.db import models

# Create your models here.
# patients/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from tenants.models import Tenant
from datetime import date

class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        UNSPECIFIED = 'U', _('Unspecified')

    # Basic Information
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    date_of_birth = models.DateField(_("Date of Birth"))
    gender = models.CharField(
        _("Gender"),
        max_length=1,
        choices=Gender.choices,
        default=Gender.UNSPECIFIED
    )
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        _("Phone Number"),
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    email = models.EmailField(_("Email Address"), blank=True)
    address = models.TextField(_("Address"), blank=True)
    
    # Medical Information
    medical_history = models.TextField(_("Medical History"), blank=True)
    allergies = models.TextField(_("Allergies"), blank=True)
    current_medications = models.TextField(_("Current Medications"), blank=True)
    insurance_id = models.CharField(
        _("Insurance ID"),
        max_length=50,
        blank=True
    )
    
    dentist = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,  # Prevents deletion of User if they have patients
        related_name='patients'
    )
    
    last_dental_visit = models.DateField(_("Last Dental Visit"), null=True, blank=True)
    dental_insurance = models.CharField(
        _("Dental Insurance Provider"),
        max_length=100,
        blank=True
    )
    
    # System Fields
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='patients'
    )
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to='patient_profiles/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['date_of_birth']),
        ]
        unique_together = [['first_name', 'last_name', 'date_of_birth', 'tenant']]

    def __str__(self):
        return f"{self.full_name} ({self.age})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))