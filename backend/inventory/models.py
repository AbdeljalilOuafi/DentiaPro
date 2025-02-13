from django.db import models

# Create your models here.
class Clinic(models.Model):
    name = models.CharField(max_length=100)
    patient_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name