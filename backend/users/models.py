from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import UserManager
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length= 255, unique=True, null=False, blank=False, verbose_name=_("Email address"))
    first_name = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("Last Name"))
    clinic_name = models.CharField(max_length=100, blank=False, null=False, default="Default Clinic", verbose_name=_("Clinic Name"))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)# ✅ Used for email verification
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()
    
    class Meta:
        app_label = "users"  # ✅ Keeps it in the public schema
        verbose_name = _("User")  # ✅ Proper naming
        verbose_name_plural = _("Users")  # ✅ Helps in Django Admin

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.fullname

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }


class OnetimePassword(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    code= models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.user.first_name}-passcode"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.fullname} Profile'


