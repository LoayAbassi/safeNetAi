from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'fraud-alerts', views.FraudAlertViewSet, basename='fraud-alert')

urlpatterns = [
    path('', include(router.urls)),
    # Security OTP endpoints
    path('security/otp/send/', views.send_security_otp, name='send_security_otp'),
    path('security/otp/verify/', views.verify_security_otp, name='verify_security_otp'),
]
