from django.db import models
from patients.models import Patient
from users.models import User
from tenants.models import Tenant

class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['start_time']
        permissions = [
            ("cancel_appointment", "Can cancel appointment"),
            ("confirm_appointment", "Can confirm appointment"),
        ]
        
    def save(self, *args, **kwargs):
        self.tenant = self.dentist.tenant
        super().save(*args, **kwargs)