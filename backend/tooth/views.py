from rest_framework import viewsets, permissions, exceptions
from .models import Tooth
from .serializers import ToothSerializer

from django_filters.rest_framework import DjangoFilterBackend


class ToothViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows universal teeth data to be viewed.
    This operates on the public schema.
    """
    queryset = Tooth.objects.all().order_by('fdi_number')
    serializer_class = ToothSerializer
    permission_classes = [permissions.IsAuthenticated] # Allow any logged-in user to read
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['arch', 'quadrant', 'is_primary', 'fdi_number', 'universal_number']
    
    
    pagination_class = None # Disables pagination since frontend team keeps bitching about it
    
    # Add search fields if needed
    # search_fields = ['universal_number', 'fdi_number', 'name']
    
    def get_serializer_context(self):
        """Add language code from URL to serializer context."""
        context = super().get_serializer_context()
        lang_code = self.kwargs.get('lang_code', 'en').lower() # Get from URL, default 'en'

        # Validate language code
        if lang_code not in ['en', 'fr']:
            # Or raise PermissionDenied, or just default
            raise exceptions.ValidationError(f"Unsupported language code: {lang_code}. Use 'en' or 'fr'.")

        context['lang_code'] = lang_code
        return context