from django.shortcuts import render

# Create your views here.
from .models import Patient
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import PatientSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.pagination import CustomPagination

class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing patient information.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  
    lookup_field = 'pk'
    
    def get_queryset(self):
        """
        This view returns a list of all patients for the current tenant.
        Optional filtering by dentist is available.
        """
        queryset = Patient.objects.filter(
            tenant=self.request.tenant
        )
        
        # Filter by dentist if specified
        dentist_id = self.request.query_params.get('dentist', None)
        if dentist_id:
            queryset = queryset.filter(dentist_id=dentist_id)
            
        # Enhanced search functionality
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                first_name__icontains=search_query
            ) | queryset.filter(
                last_name__icontains=search_query
            ) | queryset.filter(
                phone_number__icontains=search_query
            ) | queryset.filter(
                email__icontains=search_query
            )
            
        return queryset.select_related('dentist')
    
    def perform_create(self, serializer):
        """
        Set the tenant automatically based on the request
        """
        serializer.save(
            tenant=self.request.tenant,
            dentist=self.request.user
        )
        
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        # The request is already included by default, but we can ensure it's there
        context['request'] = self.request
        return context

