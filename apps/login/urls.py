# apps/login/urls.py
from django.urls import path
from .views import AlagaLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', AlagaLoginView.as_view(), name='login'),
    path('login/', AlagaLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]