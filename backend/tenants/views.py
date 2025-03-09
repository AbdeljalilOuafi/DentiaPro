from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from inventory.models import Clinic
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from .serializers import *
from users.permissions import CanManageUsers
from users.serializer import UserSerializer
from rest_framework import generics

from rest_framework.views import APIView


# Checks if the user has 'users.view_user' permission and if they do they get a list of users of the tenant
# Else they get a 403 error
class ViewTenantUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant)

# This view is for Admin's to create new users/employees ( Dentist, Receptionist )
class CreateTenantUserView(GenericAPIView):
    serializer_class = TenantUserCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user is admin
        if request.user.role != User.Role.ADMIN:
            raise PermissionDenied("Only admin users can create new users")
            
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}  # Pass request to serializer
        )
        
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({
                'status': 'OK',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'user tenant': user.tenant.name
                }
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class TenantDataView(APIView):
    def get(self, request):
        clinics = Clinic.objects.all().values('name', 'patient_count', 'created_at')
        
        return Response({
            "tenant": request.tenant.name,
            "schema": request.tenant.schema_name,
            "user": request.user.email,
            "role": request.user.role,
            "clinics": list(clinics)
        })
    
