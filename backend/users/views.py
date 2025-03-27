from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializer import *
from .permissions import *
from rest_framework.response import Response
from rest_framework import status
from .utils import send_code_to_user, resend_email
from .models import OnetimePassword
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, permissions
from .models import User, Profile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_tenants.utils import schema_context
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.views import APIView
from tenants.models import Domain

    
class DecodeTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('access_token')
        if not token:
            return Response({'error': 'No access token provided'}, status=400)

        try:
            # Decode the token
            token_backend = TokenBackend(algorithm='HS256', signing_key=settings.SECRET_KEY)
            decoded_token = token_backend.decode(token, verify=True)
            user = User.objects.get(id=decoded_token.get('user_id'))
            user_data = UserSerializer(user).data
            user_domain = Domain.objects.get(tenant=user.tenant)
            domain_data = {"clinic": user.clinic_name, "domain": user_domain.domain}
            user_data.update(domain_data)
            return Response(user_data, status=200)
        except (InvalidToken, TokenError) as e:
            return Response({'error': str(e)}, status=400)

class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = []  # Allow unauthenticated access

    def post(self, request):
        with schema_context('public'):  # Ensure we're in public schema
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                user, domain_name = serializer.save()
                
                #Use a Queue System like Celery to send emails in the backgroud, this line is bottlenecking the response
                if not settings.IS_DEVELOPMENT:                    
                    resend_email(user.email)
                
                user_serializer = UserSerializer(user)
                return Response({'status': 'OK', 'user': user_serializer.data, "domain_name": domain_name}, status.HTTP_201_CREATED)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        optcode = request.data.get("opt")
        try:
            code_obj = OnetimePassword.objects.get(code=optcode)
            user = code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'status': 'OK',
                    'detail': 'account email verified successfully'
                }, status.HTTP_200_OK)
            else:
                return Response({'status': 'NOT_OK',
                                'detail': 'User already verified'}, status.HTTP_409_CONFLICT)
        except OnetimePassword.DoesNotExist:
            return Response({'status': 'NOT_OK',
                             'detail': 'invalid code'}, status.HTTP_400_BAD_REQUEST)


class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status.HTTP_200_OK)

class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "status": f"You are corrently logged in as {user.fullname}"
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'status':'OK', 'message':'A link have been sent to your email to reset your password'}, status=status.HTTP_200_OK)


# class PasswordResetConfirm(GenericAPIView):

#     def get(self, request, uidb64, token):
#         try:
#             user_id=smart_str(urlsafe_base64_decode(uidb64))
#             user=User.objects.get(id=user_id)

#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
#             return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

#         except DjangoUnicodeDecodeError as identifier:
#             return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'status':'OK', 'message':"Password reset succesful"}, status=status.HTTP_200_OK)

class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "OK",
            "detail": "Successfully logged out"
        }, status=status.HTTP_200_OK)


class PrivateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfilePrivateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class PublicProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilePublicSerializer
    lookup_field = 'user__id'


