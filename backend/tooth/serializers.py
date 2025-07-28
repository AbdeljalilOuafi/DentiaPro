# tooth/serializers.py
from rest_framework import serializers
from .models import Tooth

class ToothSerializer(serializers.ModelSerializer):
    """
    Serializer for the shared Tooth model.
    Dynamically provides the 'name' field based on requested language.
    """
    # dynamic 'name' field
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tooth
        fields = [
            'id',
            'universal_number',
            'fdi_number',
            'palmer_notation',
            'name', # Dynamic name field
            'arch',
            'quadrant',
            'is_primary',
            # Include specific language fields if needed for debugging or specific use cases
            # 'name_en',
            # 'name_fr',
        ]
        # All fields except the dynamic 'name' are based on model fields
        # You might still want read_only_fields if you expose name_en/name_fr
        read_only_fields = ['id', 'universal_number', 'fdi_number', 'palmer_notation', 'arch', 'quadrant', 'is_primary']


    def get_name(self, obj):
        """Returns the tooth name in the language specified in the context."""
        lang_code = self.context.get('lang_code', 'en') # Default to 'en'
        return obj.get_name(lang_code=lang_code)