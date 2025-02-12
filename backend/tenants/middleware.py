from django_tenants.utils import schema_context
from django.http import JsonResponse
from tenants.models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract subdomain (e.g., dentist1 from dentist1.domain.com)
        host = request.get_host().split(".")[0]  # Adjust based on domain structure

        try:
            tenant = Tenant.objects.get(schema_name=host)
        except Tenant.DoesNotExist:
            return JsonResponse({"error": "Tenant not found", "domain": host}, status=404)

        request.tenant = tenant # Will be used by TenantMainMiddleware which is the next in the list, it no longer needs to query the domain name
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        # Ensure the logged-in user owns the tenant
        if request.user != tenant.user:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Ensure the tenant is verified (paid)
        if not request.user.is_paid:
            return JsonResponse({"error": "Payment required"}, status=402)

        return self.get_response(request)