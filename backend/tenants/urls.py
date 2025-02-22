from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateTenantUserView.as_view(), name='create-tenant-user'),
    path('', views.ViewTenantUsersView.as_view(), name='view-tenant-users'),
]
