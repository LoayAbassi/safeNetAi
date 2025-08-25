from rest_framework import viewsets, permissions
from .models import Threshold, Rule, RiskEvent
from .serializers import ThresholdSerializer, RuleSerializer

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", "") == "ADMIN"

class ThresholdViewSet(viewsets.ModelViewSet):
    queryset = Threshold.objects.all()
    serializer_class = ThresholdSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class RiskEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskEvent.objects.all().order_by("-id")
    serializer_class = None  # simple read-only, rely on DRF default representation
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
