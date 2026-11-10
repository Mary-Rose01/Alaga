from django.urls import path
from .views import health_alerts_view

urlpatterns = [
    path('health-alerts/', health_alerts_view, name='health_alerts'),
]
