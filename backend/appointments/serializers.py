from rest_framework import serializers
from .models import Appointment
from django.utils import timezone


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'dentist', 'start_time', 'end_time', 
                 'status', 'notes', 'created_at', 'updated_at']

    def validate(self, data):
        # Get the instance if this is an update
        instance = self.instance
        
        # For updates, merge incoming data with existing instance data
        if instance:
            start_time = data.get('start_time', instance.start_time)
            end_time = data.get('end_time', instance.end_time)
            dentist = data.get('dentist', instance.dentist)
        else:
            # For creation, these fields are required
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            dentist = data.get('dentist')
            if not all([start_time, end_time, dentist]):
                raise serializers.ValidationError("start_time, end_time, and dentist are required for new appointments")

        # Ensure timezone awareness only if times are provided
        if 'start_time' in data and not timezone.is_aware(data['start_time']):
            data['start_time'] = timezone.make_aware(data['start_time'])
        if 'end_time' in data and not timezone.is_aware(data['end_time']):
            data['end_time'] = timezone.make_aware(data['end_time'])

        # Validate times if either time is being updated or this is a new appointment
        if 'start_time' in data or 'end_time' in data or not instance:
            if end_time <= start_time:
                raise serializers.ValidationError("End time must be after start time")

            # Check for overlapping appointments
            overlapping_query = Appointment.objects.filter(
                dentist=dentist,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Exclude current instance if this is an update
            if instance:
                overlapping_query = overlapping_query.exclude(id=instance.id)
            
            if overlapping_query.exists():
                raise serializers.ValidationError(
                    "This time slot overlaps with another appointment"
                )

        # Validate status changes if status is being updated
        # if 'status' in data:
        #     new_status = data['status']
        #     if instance:
        #         self._validate_status_transition(instance.status, new_status)

        return data

    # def _validate_status_transition(self, current_status, new_status):
    #     """
    #     Validate that the status transition is allowed
    #     """
    #     allowed_transitions = {
    #         'SCHEDULED': ['CONFIRMED', 'CANCELLED'],
    #         'CONFIRMED': ['COMPLETED', 'CANCELLED'],
    #         'CANCELLED': [],  # No transitions allowed from cancelled
    #         'COMPLETED': []   # No transitions allowed from completed
    #     }

    #     if new_status not in allowed_transitions.get(current_status, []):
    #         raise serializers.ValidationError({
    #             'status': f"Cannot transition from {current_status} to {new_status}"
    #         })