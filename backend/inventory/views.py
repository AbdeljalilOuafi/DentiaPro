from django.shortcuts import render

# Create your views here.
from django.db import models

class Clinic(models.Model):
    name = models.CharField(max_length=100)
    patient_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name