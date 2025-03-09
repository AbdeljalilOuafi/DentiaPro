from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone_number', 'email', 'address', 'medical_history',
            'allergies', 'current_medications', 'insurance_id',
            'dentist', 'last_dental_visit', 'dental_insurance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']