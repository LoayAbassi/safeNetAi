from django.urls import path
from .views import check_transaction

urlpatterns = [
    path('check/', check_transaction),
]
