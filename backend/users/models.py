from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import UserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import  Permission

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
    
    tenant = models.ForeignKey(
    'tenants.Tenant',  # Reference to Tenant model
    on_delete=models.CASCADE,
    related_name='users',  # Access users via `tenant.users.all()`
    null=True,  # Allow null temporarily for migrations
    blank=True,
    )  
    class Role(models.TextChoices):
        # if user.role == User.Role.DENTIST compares "DENTIST" == "DENTIST"
        
        # First value is stored in DB and is what must be sent in API, second is just a display name
        # I customized the user creation to accept the role in any case and convert it to uppercase
        # so the following would work just fine if they were sent by the frontend :
        ADMIN = "ADMIN", "Admin" 
        DENTIST = "DENTIST", "Dentist"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
    
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECEPTIONIST)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()
    
    class Meta:
        app_label = "users"  # Keeps it in the public schema
        verbose_name = _("User")  # Proper naming
        verbose_name_plural = _("Users")  # Helps in Django Admin

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
        
    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if this is a new user
        super().save(*args, **kwargs)

        if is_new:  # Only assign permissions on creation
            self._assign_role_permissions()
        

    def _assign_role_permissions(self):
        # Clear existing permissions
        from django.db.models import Q

        self.user_permissions.clear()
        
        # Define permissions for each role
        
        # Edit permissions when you add more models, they need to have the name of the app at the start 
        # App name can be found under App_directory/apps.py => ModelConfig.name
        # format: appname.action_modelname. eg: 'users.add_user'
        # actions = view, add, change, delete
        
        # you can add Custom Permissions but it's not recommended you do so witouth confirmation from the team

        role_permissions = {
            self.Role.ADMIN: [
                # Users
                'users.view_user',
                'users.add_user',
                'users.change_user',
                'users.delete_user',

                
                # Appointments
                'appointments.view_appointment',
                'appointments.add_appointment',
                'appointments.change_appointment',
                'appointments.delete_appointment',
                
                # Billing
                # 'add_billing', 
                # 'change_billing', 
                # 'delete_billing',
                # # Inventory
                # 'view_reports', 'manage_inventory'
            ],
            self.Role.DENTIST: [
                'appointments.add_appointment', 'appointments.change_appointment',
                'appointments.view_appointment', 'appointments.delete_appointment'
                'users.view_user',
                # 'view_medical_records', 'add_medical_records',
                # 'view_patient', 'add_patient'
            ],
            self.Role.RECEPTIONIST: [
                'appointments.add_appointment', 'appointments.change_appointment',
                # 'view_patient', 'add_patient',
                # 'view_billing'
            ]
        }

        # Get permissions for the user's role
        # if self.role in role_permissions:
        #     permissions = Permission.objects.filter(codename__in=role_permissions[self.role])
        #     self.user_permissions.add(*permissions)
        
        if self.role in role_permissions:
            permissions_to_add = role_permissions[self.role]
            q_objects = Q()
            for perm in permissions_to_add:
                print(perm)
                app_label, codename = perm.split('.', 1)
                q_objects |= Q(content_type__app_label=app_label, codename=codename)

            permissions = Permission.objects.filter(q_objects)
            self.user_permissions.add(*permissions)


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


