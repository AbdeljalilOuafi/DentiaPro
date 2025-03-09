
from rest_framework import serializers
from users.models import User, Profile
from django.db import transaction
import logging

# Set up logger
logger = logging.getLogger(__name__)

class TenantUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    # role = serializers.ChoiceField(choices=User.Role.choices)
    role = serializers.CharField()  # Accept any case

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "role"]
        
    def validate_role(self, value):
        # Convert to uppercase before validation
        uppercase_role = value.upper()
        if uppercase_role not in User.Role.values:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {User.Role.values}")
        return uppercase_role

    def create(self, validated_data):
        # Get the current tenant from the context
        # Get the current tenant from the context
        request = self.context.get('request')
        if not request:
            logger.error("No request found in context")
            raise serializers.ValidationError("No request found in context")
            
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            logger.error("Tenant not found in request")
            raise serializers.ValidationError("Tenant not found in request")
        
        # Log before transaction
        logger.info(f"Creating user for tenant: {tenant}")
        logger.info(f"Current user: {request.user}")

        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                password=validated_data['password'],
                role=validated_data['role'],
                tenant=tenant,  # Associate with current tenant
                clinic_name=tenant.name  # Use the tenant's clinic name
            )
            
            Profile.objects.create(user=user)
            
            return user