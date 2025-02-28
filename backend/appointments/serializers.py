from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'dentist', 'start_time', 'end_time', 
                 'status', 'notes', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure end time is after start time
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time")
        
        # Check for overlapping appointments for the dentist
        overlapping = Appointment.objects.filter(
            dentist=data['dentist'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exclude(id=self.instance.id if self.instance else None)
        
        if overlapping.exists():
            raise serializers.ValidationError("This time slot overlaps with another appointment")
        
        return data