
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # for advanced filtering

# Import models and serializers from this app
from .models import ProcedureCategory, ProcedureType, Procedure
from .serializers import (
    ProcedureCategorySerializer,
    ProcedureTypeSerializer,
    ProcedureSerializer
)

class TenantSpecificViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that ensures objects are scoped to the current tenant.
    Assumes default TenantManager correctly filters querysets.
    """
    permission_classes = [permissions.IsAuthenticated] # Add more specific permissions later if needed

    def get_queryset(self):
        # The default manager for tenant models should automatically filter
        # by the current tenant based on the request middleware.
        # If not, you'd manually filter here:
        # user = self.request.user
        # tenant = self.request.tenant # Provided by django-tenants middleware
        # return self.queryset.filter(tenant=tenant)
        return super().get_queryset()

    def get_serializer_context(self):
        """Pass request to serializer context for dynamic querysets."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # Optional: You might want to ensure tenant is set on create/update explicitly
    # def perform_create(self, serializer):
    #     serializer.save(tenant=self.request.tenant)

    # def perform_update(self, serializer):
    #     serializer.save(tenant=self.request.tenant)


class ProcedureCategoryViewSet(TenantSpecificViewSet):
    """API endpoint for tenant Procedure Categories."""
    queryset = ProcedureCategory.objects.all().order_by('name')
    serializer_class = ProcedureCategorySerializer
    # filter_backends = [DjangoFilterBackend] # Optional
    # filterset_fields = ['name'] # Optional


class ProcedureTypeViewSet(TenantSpecificViewSet):
    """API endpoint for tenant Procedure Types."""
    queryset = ProcedureType.objects.select_related('category').order_by('category__name', 'name')
    serializer_class = ProcedureTypeSerializer
    filter_backends = [DjangoFilterBackend] # Optional
    filterset_fields = ['name', 'category', 'standard_code', 'is_active']

    def get_queryset(self):
        """Optionally filter by 'is_active' for list view."""
        queryset = super().get_queryset()
        if self.action == 'list':
            is_active_param = self.request.query_params.get('is_active')
            if is_active_param in ['all']:
                return queryset
            elif is_active_param is None: 
                 queryset = queryset.filter(is_active=True) # Default to showing only active types in list
        return queryset



class ProcedureViewSet(TenantSpecificViewSet):
    """API endpoint for tenant Procedures."""
    queryset = Procedure.objects.select_related(
        'patient', 'procedure_type', 'tooth', 'dentist', 'appointment' # Optimize queries
    ).order_by('-procedure_date', '-created_at')
    serializer_class = ProcedureSerializer
    filter_backends = [DjangoFilterBackend] # Optional
    filterset_fields = ['patient', 'procedure_type', 'tooth', 'status', 'dentist', 'appointment'] # Optional
    # search_fields = ['patient__first_name', 'patient__last_name', 'procedure_type__name', 'notes'] # Optional

    # Add filtering specific to date ranges etc. if needed via filtersets