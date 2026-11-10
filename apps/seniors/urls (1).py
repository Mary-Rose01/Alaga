from django.urls import path
from .views import bhw_workload_view

urlpatterns = [
    path('bhw-workload/', bhw_workload_view, name='bhw_workload'),
]
