from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.risk.admin_views import (
    ThresholdViewSet, 
    RuleViewSet, 
    ClientProfileAdminViewSet,
    TransactionAdminViewSet,
    FraudAlertAdminViewSet
)
from apps.transactions.views import TransactionViewSet, FraudAlertViewSet
from apps.users.views import ClientProfileViewSet, AdminClientProfileViewSet, VerifyOTPView
from apps.users.auth_views import login_view, register_view, verify_otp_view, resend_otp_view
from apps.risk.views import predict_fraud

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
    path("api/auth/login/", login_view, name='login'),
    path("api/auth/register/", register_view, name='register'),
    path("api/auth/verify-otp/", verify_otp_view, name='verify-otp'),
    path("api/auth/resend-otp/", resend_otp_view, name='resend-otp'),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name='token-refresh'),
    
    # Client API endpoints
    path("api/client/", include(client_router.urls)),
    
    # Admin API endpoints
    path("api/admin/", include(admin_router.urls)),
    
    # AI endpoints
    path("api/ai/predict/", predict_fraud, name='predict-fraud'),
    
    # System management endpoints (admin only)
    path("api/system/", include('apps.system.urls')),
]
