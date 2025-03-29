from rest_framework import serializers
from .models import AIConversation

class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = ['id', 'question', 'answer', 'created_at']
        read_only_fields = ['answer', 'created_at']