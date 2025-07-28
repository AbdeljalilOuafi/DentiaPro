from rest_framework import serializers
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError # Avoid name clash

# Import models
from .models import ProcedureCategory, ProcedureType, Procedure
from patients.models import Patient
from appointments.models import Appointment
from tooth.models import Tooth
from users.models import User

# --- Procedure Category ---
class ProcedureCategorySerializer(serializers.ModelSerializer):
    """Serializer for tenant-specific Procedure Categories."""
    class Meta:
        model = ProcedureCategory
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

# --- Procedure Type ---
class ProcedureTypeSerializer(serializers.ModelSerializer):
    """Serializer for tenant-specific Procedure Types."""
    # Display category name on read, accept ID on write
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProcedureCategory.objects.all(), # Queryset potentially refined in view
        allow_null=True,
        required=False,
        write_only=True
    )
    
    # Returns a json of the category object
    # Didn't find it neccessary so im returning only the category name for display purpose 
    # category = ProcedureCategorySerializer(read_only=True) 

    class Meta:
        model = ProcedureType
        fields = [
            'id',
            'category', # Write-only FK
            'category_name', # Read-only name
            'name',
            'description',
            'internal_code',
            'standard_code',
            'default_price',
            'default_duration',
            'requires_tooth',
            'requires_surface',
            'is_active',
        ]
        read_only_fields = ['id']

    def validate_category(self, value):
        # Ensure the selected category belongs to the current tenant.
        # This basic check assumes the queryset passed from the view is correct.
        # More robust validation might involve accessing request context if passed.
        if value and not ProcedureCategory.objects.filter(pk=value.pk).exists():
             raise serializers.ValidationError("Selected category not found for this tenant.")
        return value

# --- Procedure ---
class ProcedureSerializer(serializers.ModelSerializer):
    """Serializer for tenant-specific Procedure instances."""

    # Read-only fields for related object details
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    procedure_type_name = serializers.CharField(source='procedure_type.name', read_only=True)
    tooth_info = serializers.CharField(source='tooth.__str__', read_only=True, allow_null=True) # Use Tooth's __str__
    dentist_name = serializers.CharField(source='dentist.fullname', read_only=True, allow_null=True) # Assumes User has it
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Writable fields for relationships (using PrimaryKeyRelatedField)
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all() # Base queryset, will be filtered in view
    )
    procedure_type = serializers.PrimaryKeyRelatedField(
        queryset=ProcedureType.objects.filter(is_active=True) # Base queryset, filtered in view
    )
    tooth = serializers.PrimaryKeyRelatedField(
        queryset=Tooth.objects.all(), # Public teeth, no tenant filtering needed
        allow_null=True,
        required=False # Only required if procedure_type.requires_tooth is True (validated below)
    )
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), # Base queryset, filtered in view <<< UNCOMMENT IF NEEDED
        allow_null=True,
        required=False
    )
    dentist = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), # Base queryset, filtered in view
        allow_null=True,
        required=False
    )

    class Meta:
        model = Procedure
        fields = [
            'id',
            'patient', # Writable FK
            'patient_name', # Read-only detail
            'appointment', # Writable FK (Optional)
            'procedure_type', # Writable FK
            'procedure_type_name', # Read-only detail
            'tooth', # Writable FK (Optional)
            'tooth_info', # Read-only detail
            'tooth_surfaces',
            'status',
            'status_display', # Read-only detail
            'procedure_date',
            'completion_date',
            'dentist', # Writable FK (Optional)
            'dentist_name', # Read-only detail
            'price',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'completion_date', # Typically set by logic based on status
            'created_at',
            'updated_at',
            'patient_name',
            'procedure_type_name',
            'tooth_info',
            'dentist_name',
            'status_display',
        ]

    # def __init__(self, *args, **kwargs):
    #     # Dynamically filter querysets based on the current tenant (passed in context)
    #     super().__init__(*args, **kwargs)
    #     request = self.context.get('request', None)
    #     if request and hasattr(request, 'tenant'):
    #         tenant = request.tenant
    #         # Assuming Patient, Appointment, ProcedureType, Provider models are correctly filtered by tenant manager
    #         self.fields['patient'].queryset = Patient.objects.filter(tenant=tenant) # Adjust tenant filter if needed
    #         self.fields['procedure_type'].queryset = ProcedureType.objects.filter(tenant=tenant, is_active=True)
    #         # self.fields['appointment'].queryset = Appointment.objects.filter(tenant=tenant) # <<< UNCOMMENT IF NEEDED
    #         # Filter providers if necessary (e.g., only users associated with the tenant)
    #         # self.fields['provider'].queryset = settings.AUTH_USER_MODEL.objects.filter(...)

    def validate(self, data):
        """
        Apply model-level validation logic.
        """
        # Get related instances for validation checks
        procedure_type = data.get('procedure_type', getattr(self.instance, 'procedure_type', None))
        tooth = data.get('tooth', getattr(self.instance, 'tooth', None))
        tooth_surfaces = data.get('tooth_surfaces', getattr(self.instance, 'tooth_surfaces', None))
        status = data.get('status', getattr(self.instance, 'status', None))
        completion_date = data.get('completion_date', getattr(self.instance, 'completion_date', None))

        errors = {}

        # Check tooth requirement
        if procedure_type and procedure_type.requires_tooth and not tooth:
            errors['tooth'] = f"A tooth must be specified for procedure type '{procedure_type.name}'."

        # Check surfaces requirement (optional strictness)
        # if procedure_type and procedure_type.requires_surface and not tooth_surfaces:
        #     errors['tooth_surfaces'] = f"Tooth surfaces must be specified for procedure type '{procedure_type.name}'."

        if tooth_surfaces and not tooth:
            errors.setdefault('tooth', []).append("A tooth must be selected if surfaces are specified.") # Use setdefault for multiple errors

        # Validate status/completion date consistency (example)
        if status == Procedure.Status.COMPLETED and not completion_date and not self.instance: # Only enforce on create if not auto-set
             # Note: The model's save method usually handles setting this automatically
             pass
        if status != Procedure.Status.COMPLETED and completion_date:
             errors['completion_date'] = "Completion date should only be set automatically when the status updates to 'Completed'"


        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        # Auto-set price from type if not provided
        if 'price' not in validated_data and validated_data.get('procedure_type'):
            validated_data['price'] = validated_data['procedure_type'].default_price
            
        # auto set procedure date from the appointment if not provided
        if 'procedure_date' not in validated_data and validated_data.get('appointment'):
            validated_data['procedure_date'] = validated_data['appointment'].start_time
        return super().create(validated_data)