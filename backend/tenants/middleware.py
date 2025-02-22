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
        
        
        print("==== Debug Permission Information ====")
        print(f"User: {request.user}")
        print(f"User permissions: {request.user.get_all_permissions()}")  # This will show all permissions
        print(f"Has view_user permission: {request.user.has_perm('users.view_user')}")
        
        print("==== User Specific Debug Infomation ====")
        print(f'user: {request.user.email}')
        print(f'tenant: {request.user.tenant.name}') # This line is causing a crash for users created 
        print(f'role: {request.user.role}')
        

        
        # If we're dealing with public tenant, just return
        if current_tenant.schema_name == 'public':
            return response
        

        try:
        #     # Ensure user is authenticated if token is present
        #     if 'Authorization' in request.headers:
        #         try:
        #             jwt_auth = JWTAuthentication()
        #             validated_token = jwt_auth.get_validated_token(
        #                 request.headers['Authorization'].split(' ')[1]
        #             )
        #             # Get user with select_related to ensure tenant is loaded
        #             user = jwt_auth.get_user(validated_token)
        #             request.user = user
        #             print(user)
        #             print("User has been assigned to the request")
        #             print(f"Request user after manual assignment: {request.user}")
        #         except Exception as e:
        #             print(f"Token validation error: {str(e)}")
        #             return JsonResponse({"error": "Invalid authentication token"}, status=401)
            
        #     # Handle authentication check
            if isinstance(request.user, AnonymousUser):
                if not self._is_allowed_anonymous_url(request):
                    return JsonResponse({"error": "Authentication required, Login and try again"}, status=401)
                return response
            
            # if not request.user.tenant:
            #     return JsonResponse({"you fucked boy": "this user actually have no tenant attached to it. take a fucking look at CreateTenantUserView"})
            # elif request.user.tenant:
            #     return JsonResponse({'user': request.user.email,
            #                          'tenant': request.user.tenant.name,
            #                          'role': request.user.role})

            
            user_domain = Domain.objects.get(tenant=request.user.tenant)
            
            # User validation
            if request.user.tenant != current_tenant:
                return JsonResponse({"error": "Invalid tenant access, Please use your assigned domain",
                                    "current": current_domain,
                                    "allowed": user_domain.domain.lower()}, status=403)
            # Domain validation
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
            
            
            # Verify Payment, make sure this check is only ran on the first Register, not on employees
            # if not request.user.is_paid:
            #     return JsonResponse({"error": "Payment required"}, status=402)
            
            return response
            
        except Exception as e:
            print(f"Middleware error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({"error": f"Access denied: {str(e)}"}, status=403)
    
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