from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AIConversation
from .serializers import AIConversationSerializer
from .utils import get_response
from rest_framework.permissions import IsAuthenticated
from .utils import GeminiAPIError

class AIConversationViewSet(viewsets.ModelViewSet):
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(
            tenant=self.request.tenant,
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        # Get AI response
        question = serializer.validated_data['question']        
        try:
            answer = get_response(question)
            
            # Save conversation
            serializer.save(
                tenant=self.request.tenant,
                user=self.request.user,
                answer=answer
            )
        except GeminiAPIError as e:
            raise e
        except Exception as e:
            # For any other unexpected errors
            raise GeminiAPIError(detail="An unexpected error occurred")