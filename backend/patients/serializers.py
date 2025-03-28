from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    profile_picture_file = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone_number', 'email', 'address', 'medical_history',
            'allergies', 'current_medications', 'insurance_id',
            'dentist', 'last_dental_visit', 'dental_insurance', 'created_at', 'updated_at',
            'profile_picture', 'profile_picture_file'
        ]
        read_only_fields = ['created_at', 'updated_at', 'profile_picture']
        

    def validate_profile_picture_file(self, value):
        if value:
            # Validate file size (optional since Cloudinary will handle this but ya never know )
            if value.size > 10 * 1024 * 1024:  # 10MB limit
                raise serializers.ValidationError("Image file too large ( > 10MB )")
        return value
    
    def create(self, validated_data):
        # Remove profile_picture_file from validated_data as it's not a model field
        profile_picture_file = validated_data.pop('profile_picture_file', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Remove profile_picture_file from validated_data as it's not a model field
        profile_picture_file = validated_data.pop('profile_picture_file', None)
        return super().update(instance, validated_data)