from django.urls import path
from .views import reports_view

urlpatterns = [
    path('reports/', reports_view, name='reports'),
]
