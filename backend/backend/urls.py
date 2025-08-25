from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.risk.admin_views import ThresholdViewSet, RuleViewSet, RiskEventViewSet
from apps.risk.views import quote, initiate, confirm, my_accounts
from apps.users.auth_views import LoginView, RegisterView

router = DefaultRouter()
router.register(r"risk/thresholds", ThresholdViewSet, basename="threshold")
router.register(r"risk/rules", RuleViewSet, basename="rule")
router.register(r"risk/events", RiskEventViewSet, basename="riskevent")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login", LoginView.as_view()),
    path("api/auth/register", RegisterView.as_view()),
    path("api/me/accounts", my_accounts),
    path("api/transactions/quote", quote),
    path("api/transactions/initiate", initiate),
    path("api/transactions/confirm", confirm),
    path("api/", include(router.urls)),
]
