from django.shortcuts import render
from .serializers import *
from .permissions import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from datetime import datetime, timedelta


# Create your views here.
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [CanManageAppointments]
    
    def get_queryset(self):
        queryset = Appointment.objects.filter(
            tenant=self.request.tenant
        )
        
        # Handle calendar view parameters
        start_date = self.request.query_params.get('start', None)
        end_date = self.request.query_params.get('end', None)
        view_type = self.request.query_params.get('view', 'month')
        
        if start_date and end_date:
            # Convert string dates to datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(start_time__date__range=[start_date, end_date])
        
        # Filter by dentist if specified
        dentist_id = self.request.query_params.get('dentist', None)
        if dentist_id:
            queryset = queryset.filter(dentist_id=dentist_id)
            
        return queryset.select_related('patient', 'dentist')

    @action(detail=False, methods=['get'])
    def calendar_slots(self, request):
        """
        Return available time slots for a given date range
        """
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        dentist_id = request.query_params.get('dentist')
        
        if not all([start_date, end_date, dentist_id]):
            return Response(
                {"error": "start, end, and dentist parameters are required"}, 
                status=400
            )
            
        # Get booked appointments
        booked_slots = Appointment.objects.filter(
            tenant=request.tenant,
            dentist_id=dentist_id,
            start_time__date__range=[start_date, end_date]
        ).values('start_time', 'end_time')
        
        # Generate all possible slots
        all_slots = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                for hour in range(9, 17):  # 9 AM to 5 PM
                    slot_start = current_date.replace(hour=hour, minute=0)
                    slot_end = slot_start + timedelta(minutes=60)
                    
                    # Check if slot is available
                    is_available = not any(
                        booked.start_time <= slot_start < booked.end_time
                        for booked in booked_slots
                    )
                    
                    if is_available:
                        all_slots.append({
                            'start': slot_start.isoformat(),
                            'end': slot_end.isoformat(),
                            'available': True
                        })
                        
            current_date += timedelta(days=1)
            
        return Response(all_slots)