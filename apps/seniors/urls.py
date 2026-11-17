from django.urls import path

from .views import bhw_workload_view, senior_list_view, senior_register_view

urlpatterns = [
    path('seniors/', senior_list_view, name='senior_list'),
    path('seniors/register/', senior_register_view, name='senior_register'),
    path('bhw-workload/', bhw_workload_view, name='bhw_workload'),
]
