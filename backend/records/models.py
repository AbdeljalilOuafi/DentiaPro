from django.db import models
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

from patients.models import Patient
from appointments.models import Appointment
from tooth.models import Tooth
from users.models import User


# Make sure this app ('procedures') is in TENANT_APPS in settings.py
class ProcedureCategory(models.Model):
    """
    Tenant-specific category for grouping procedure types (e.g., Restorative, Surgical).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) # Unique within the tenant
    description = models.TextField(blank=True, null=True)
    # tenant = models.ForeignKey(settings.TENANT_MODEL, on_delete=models.CASCADE) # django-tenants handles this automatically

    class Meta:
        verbose_name = "Procedure Category"
        verbose_name_plural = "Procedure Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProcedureType(models.Model):
    """
    Defines a type of procedure offered by a specific tenant (practice),
    including default pricing, codes, and properties.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ProcedureCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="procedure_types",
        help_text="Optional category for organization."
    )
    name = models.CharField(
        max_length=200,
        unique=True, # Unique name within the tenant
        help_text="Name of the procedure type (e.g., 'Composite Filling - 1 Surface', 'Regular Checkup')."
    )
    description = models.TextField(blank=True, null=True)
    internal_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        # unique=True, # Consider if internal codes must be unique per tenant
        help_text="Practice-specific code for this procedure type."
    )
    standard_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True, # Often searched/filtered by standard codes
        help_text="Standardized code (e.g., CDT, CPT) if applicable."
    )
    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Default price for this procedure type. Actual price may vary per instance."
    )
    default_duration = models.DurationField(
        blank=True,
        null=True,
        help_text="Estimated default duration for scheduling purposes (e.g., 0:30:00 for 30 mins)."
    )
    requires_tooth = models.BooleanField(
        default=True,
        help_text="Does this procedure typically apply to a specific tooth?"
    )
    requires_surface = models.BooleanField(
        default=False,
        help_text="Does this procedure typically involve specific tooth surfaces (e.g., fillings)?"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Is this procedure type currently offered by the practice?"
    )
    # tenant = models.ForeignKey(settings.TENANT_MODEL, on_delete=models.CASCADE) # Handled by django-tenants

    class Meta:
        verbose_name = "Procedure Type"
        verbose_name_plural = "Procedure Types"
        ordering = ['category__name', 'name'] # Order by category then name

    def __str__(self):
        code = self.standard_code or self.internal_code
        return f"{self.name}{f' [{code}]' if code else ''}"


class Procedure(models.Model): # 5 Relationships !!!
    """
    Represents an instance of a dental procedure performed or planned for a patient.
    Linked to a patient, optionally an appointment, a procedure type, and potentially a tooth.
    """
    class Status(models.TextChoices):
        PLANNED = 'PL', 'Planned'           # Needs to be done, not yet scheduled
        SCHEDULED = 'SC', 'Scheduled'       # Assigned to an appointment
        IN_PROGRESS = 'IP', 'In Progress'   # Currently being worked on
        COMPLETED = 'CO', 'Completed'       # Finished
        CANCELLED = 'CA', 'Cancelled'       # Will not be done
        ON_HOLD = 'OH', 'On Hold'           # Temporarily postponed

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT, # Prevent deleting patient if procedures exist? Or CASCADE? Discuss implications.
        related_name="procedures",
        db_index=True
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL, # If appointment is deleted, keep the procedure record but unlink it
        null=True,
        blank=True,
        related_name="procedures",
        db_index=True,
        help_text="The appointment during which this procedure is scheduled or was performed."
    )
    procedure_type = models.ForeignKey(
        ProcedureType,
        on_delete=models.PROTECT, # Prevent deleting a ProcedureType if instances exist
        related_name="instances",
        help_text="The type of procedure performed or planned."
    )
    # Cross-schema ForeignKey: Links tenant schema (Procedure) to public schema (Tooth)
    tooth = models.ForeignKey(
        Tooth,
        on_delete=models.PROTECT, # Don't delete standard teeth
        null=True,
        blank=True,
        related_name="procedures", # Allows Tooth.procedures.all() (filtered by current tenant context)
        # db_constraint=False, # Usually not needed, django-tenants handles it. Add if you encounter FK constraint errors across schemas.
        help_text="Specific tooth this procedure applies to, if any."
    )
    tooth_surfaces = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Comma-separated list of tooth surfaces involved (e.g., M,O,D,B,L,I)."
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
        help_text="Current status of the procedure."
    )
    procedure_date = models.DateTimeField(
        # if not provided it populates based on appointment start date.
        db_index=True,
        null=True,
        blank=True,
        help_text="Date and time the procedure is planned, scheduled, or was completed.",
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time the procedure was marked as completed."
    )
    dentist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_procedures",
        help_text="The dentist who performed or is scheduled to perform the procedure."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual price charged for this specific procedure instance."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Clinical or administrative notes specific to this procedure instance."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # tenant = models.ForeignKey(settings.TENANT_MODEL, on_delete=models.CASCADE) # Handled by django-tenants

    class Meta:
        verbose_name = "Procedure"
        verbose_name_plural = "Procedures"
        ordering = ['-procedure_date', '-created_at'] # Show most recent first
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['appointment']),
            models.Index(fields=['procedure_type', 'status']),
        ]

    def __str__(self):
        tooth_info = f" Tooth {self.tooth.fdi_number}" if self.tooth else ""
        return f"{self.procedure_type.name}{tooth_info} for {self.patient} on {self.procedure_date.strftime('%Y-%m-%d')} ({self.get_status_display()})"

    def clean(self):
        """
        Add custom validation logic.
        """
        super().clean()
        # Validate tooth requirement
        if self.procedure_type and self.procedure_type.requires_tooth and not self.tooth:
            raise ValidationError({
                'tooth': f"A tooth must be specified for procedure type '{self.procedure_type.name}'."
            })
        # Validate surface requirement (optional - depends if you make requires_surface strict)
        # if self.procedure_type.requires_surface and not self.tooth_surfaces:
        #     raise ValidationError({
        #         'tooth_surfaces': f"Tooth surfaces must be specified for procedure type '{self.procedure_type.name}'."
        #     })
        # Ensure tooth is specified if surfaces are given
        if self.tooth_surfaces and not self.tooth:
             raise ValidationError({
                'tooth': "A tooth must be selected if surfaces are specified."
             })
        # Ensure completion date logic is sound
        if self.status == self.Status.COMPLETED and not self.completion_date:
            raise ValidationError("Completion date must be set when status is 'Completed'. It will be set automatically on save if blank.")
        if self.status != self.Status.COMPLETED and self.completion_date:
             raise ValidationError("Completion date should only be set if status is 'Completed'. It will be cleared automatically on save if status is not 'Completed'.")


    def save(self, *args, **kwargs):
        # Auto-populate price from type if creating new and price not explicitly set
        # Be careful: check if 'price' was provided in kwargs or if self.price is None?
        # This simple check works if price isn't manually set to None.
        if not self.pk and self.price is None and self.procedure_type:
             self.price = self.procedure_type.default_price

        # Update completion date based on status
        if self.status == self.Status.COMPLETED and not self.completion_date:
             self.completion_date = timezone.now()
        elif self.status != self.Status.COMPLETED:
             self.completion_date = None # Clear completion date if status changes away from completed

        # Run full validation before saving
        self.full_clean()
        super().save(*args, **kwargs)