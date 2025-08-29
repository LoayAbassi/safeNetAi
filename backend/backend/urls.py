from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.risk.admin_views import (
    ThresholdViewSet, 
    RuleViewSet, 
    ClientProfileAdminViewSet,
    TransactionAdminViewSet,
    FraudAlertAdminViewSet
)
from apps.transactions.views import TransactionViewSet, FraudAlertViewSet
from apps.users.views import ClientProfileViewSet, AdminClientProfileViewSet
from apps.users.auth_views import LoginView, RegisterView

# Client routers
client_router = DefaultRouter()
client_router.register(r'profile', ClientProfileViewSet, basename='client-profile')
client_router.register(r'transactions', TransactionViewSet, basename='client-transaction')
client_router.register(r'fraud-alerts', FraudAlertViewSet, basename='client-fraud-alert')

# Admin routers
admin_router = DefaultRouter()
admin_router.register(r'clients', AdminClientProfileViewSet, basename='admin-client')
admin_router.register(r'thresholds', ThresholdViewSet, basename='threshold')
admin_router.register(r'rules', RuleViewSet, basename='rule')
admin_router.register(r'transactions', TransactionAdminViewSet, basename='admin-transaction')
admin_router.register(r'fraud-alerts', FraudAlertAdminViewSet, basename='admin-fraud-alert')

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Authentication endpoints
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/register/", RegisterView.as_view()),
    
    # Client API endpoints
    path("api/client/", include(client_router.urls)),
    
    # Admin API endpoints
    path("api/admin/", include(admin_router.urls)),
]
