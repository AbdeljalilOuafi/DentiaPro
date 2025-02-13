from django.http import JsonResponse
from django_tenants.middleware import TenantMainMiddleware
from django.contrib.auth.models import AnonymousUser
from django_tenants.utils import get_tenant_domain_model, get_public_schema_name
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.middleware import get_user
from django.apps import apps

# Import models at the class level
Tenant = apps.get_model('tenants', 'Tenant')

class CustomTenantMiddleware(TenantMainMiddleware):  
    def __call__(self, request):

        exempt_paths = [
            '/api/auth/register/',
            '/api/auth/verify-email/',
            '/api/auth/login/',
            '/api/auth/password-reset/',
            '/api/auth/password-reset-confirm/',
            '/api/auth/set-new-password/',
            '/api/auth/logout/'
        ]

        # Skip tenant logic for exempt paths (no domain/schema checks)
        if any(request.path.startswith(path) for path in exempt_paths):
            # Bypass tenant validation and directly return the response
            return self.get_response(request)

        # Proceed with tenant validation for non-exempt paths
        response = super().__call__(request)
                
        current_tenant = request.tenant
        Domain = get_tenant_domain_model()
        current_domain = request.get_host().split(':')[0].lower()
        tenant_domain = Domain.objects.get(tenant=current_tenant).domain
        
        print("==== Debug Information ====")
        print(f"Current tenant from request: {current_tenant}")
        print(f"Curent domain: {current_domain}")
        print(f"Tenant domain: {tenant_domain}")
        
        # This prints AnonymousUser for some reason ??
        # print(f"Request user: {request.user}")
        
        # If we're dealing with public tenant, just return
        # if current_tenant.schema_name == 'public':
        #     return response
            
        try:
            # Ensure user is authenticated if token is present
            if 'Authorization' in request.headers:
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(
                        request.headers['Authorization'].split(' ')[1]
                    )
                    # Get user with select_related to ensure tenant is loaded
                    user = jwt_auth.get_user(validated_token)
                    request.user = user
                    print(f"Request user after manual assignment: {request.user}")
                except Exception as e:
                    print(f"Token validation error: {str(e)}")
                    return JsonResponse({"error": "Invalid authentication token"}, status=401)
            
            # Handle authentication check
            if isinstance(request.user, AnonymousUser):
                if not self._is_allowed_anonymous_url(request):
                    return JsonResponse({"error": "Authentication required"}, status=401)
                return response
            
            # User validation
            if request.user.tenant != current_tenant:
                return JsonResponse({"error": "Invalid tenant access"}, status=403)
            # Domain validation
            user_domain = Domain.objects.get(tenant=request.user.tenant)
            try:
                if current_domain != user_domain.domain.lower():
                    return JsonResponse({
                        "error": "Invalid domain access",
                        "current": current_domain,
                        "allowed": user_domain.domain.lower()
                    }, status=403)
                
            except Domain.DoesNotExist:
                print(f"Domain not found for tenant: {request.user.tenant}")
                return JsonResponse({"error": "Domain configuration error"}, status=403)
            
            if not request.user.is_paid:
                return JsonResponse({"error": "Payment required"}, status=402)
            
            return response
            
        except Exception as e:
            print(f"Middleware error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({"error": "Access denied"}, status=403)
    
    def _is_public_url(self, request):
        public_urls = [
            '/api/auth/',
            '/admin/',
            '/api/token/',
            '/api/token/refresh/'
            'api/auth/password-reset-confirm/',
        ]
        return any(request.path.startswith(url) for url in public_urls)
    
    def _is_allowed_anonymous_url(self, request):
        anonymous_urls = [
            '/api/auth/login/',
            '/api/auth/verify-email/',
            '/api/auth/password-reset/',
            '/api/auth/logout/',
            '/api/auth/register/',
            '/api/token/',
            '/api/token/refresh/',
            '/api/auth/set-new-password/', 
            '/api/auth/password-reset-confirm/'
        ]
        return any(request.path.startswith(url) for url in anonymous_urls)