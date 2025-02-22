from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import Profile
from django.conf import settings
from tenants.models import Tenant, Domain
from django.db import transaction
import uuid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'fullname', 'role']


class PublicUserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'fullname']

class ProfilePublicSerializer(serializers.ModelSerializer):
    user = PublicUserProfileSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'image']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=8, write_only=True)
    clinic_name = serializers.CharField(max_length=100)  # Add this field


    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "password2", "clinic_name"]

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')

        if password != password2:
            serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2', None)
        
        schema_name = f"tenant_{uuid.uuid4().hex}"  # e.g., "tenant_1a2b3c4d5e..."
        
        with transaction.atomic():
            tenant = Tenant.objects.create(
                user=user,
                name=validated_data['clinic_name'],  # Use clinic_name instead of first_name
                schema_name = schema_name,  # Makes sure schema_name is unique
                paid_until=None  # We can set a trial period date here
            )
            tenant.save()
            
            user = User.objects.create_user(
                email=validated_data.get('email'),
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                password=validated_data.get('password'),
                clinic_name=validated_data.get('clinic_name'),
                tenant=tenant,
                role=User.Role.ADMIN  # Set role to ADMIN by default on the Register endpoint since it's a new user
            )
            user.save()  # Ensures user.id is generated

            Profile.objects.create(user=user)
            

            
            domain_name = f"{user.clinic_name.lower().replace(' ', '-')}.vercel.app"  # Sanitize domain name
            
            Domain.objects.create(
                tenant=tenant,
                domain=domain_name,
                is_primary=True
            )

        return (user, domain_name) 



class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255, min_length=6)
    password=serializers.CharField(max_length=68 ,write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        # Line 46 where the error is coming from is below
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")
        # if not user.is_verified:
        #     raise AuthenticationFailed("Email is not verified")
        # if not user.is_paid:
        #     raise AuthenticationFailed("The service is not paid, redirect to the payment page")

        user_tokens = user.tokens()
        return {
            'email': user.email,
            'full_name': user.fullname,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):

        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user= User.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            
            # No need for these anymore since the email will include a link to thr frontend not backend
            # current_site=get_current_site(request).domain
            # relative_link =reverse('reset-password-confirm', kwargs={'uidb64':uidb64, 'token':token})
            
            frontend_url = "http://localhost:8000"
            reset_url = f"{frontend_url}/reset-password/{uidb64}/{token}"
            print(reset_url)
            email_body=f"Hi {user.first_name} use the link below to reset your password {reset_url}"
            data={
                'email_body':email_body,
                'email_subject':"Reset your Password",
                'to_email':user.email
                }
            send_normal_email(data)

        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64=serializers.CharField(min_length=1, write_only=True)
    token=serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token=attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")


class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')


class UserPrivateSerializer(serializers.ModelSerializer):
    date_joined = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'fullname', 'date_joined', 'last_login']
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']

    def get_date_joined(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S')

    def get_last_login(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M:%S')


class ProfilePrivateSerializer(serializers.ModelSerializer):
    user = UserPrivateSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'image']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        # Update User model fields
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update Profile model fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if 'image' in validated_data:
            instance.image = validated_data['image']
            
        instance.save()
        return instance





