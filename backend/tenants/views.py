from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from inventory.models import Clinic

def tenant_data_test(request):
    # Get data from tenant-specific schema
    clinics = Clinic.objects.all().values('name', 'patient_count', 'created_at')
    
    # Also show tenant info for verification
    return JsonResponse({
        "tenant": request.tenant.name,
        "schema": request.tenant.schema_name,
        "clinics": list(clinics)
    })