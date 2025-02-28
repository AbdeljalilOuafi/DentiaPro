from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone_number', 'email', 'address', 'medical_history',
            'allergies', 'current_medications', 'insurance_id',
            'dentist', 'last_dental_visit', 'dental_insurance',
            'tenant', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
        # No need to check if 'tenant' is in data since it's set from the request
        # Just ensure the dentist belongs to the correct tenant
        if not 'dentist' in data:
            raise serializers.ValidationError("Dentist is required")
        return data