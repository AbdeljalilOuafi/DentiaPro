from rest_framework.routers import DefaultRouter
from .views import AIConversationViewSet

router = DefaultRouter()
router.register(r'chat', AIConversationViewSet, basename='ai-chat')

urlpatterns = router.urls