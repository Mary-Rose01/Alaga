from django.urls import path
from .views import AlagaLoginView, register_view, home_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', AlagaLoginView.as_view(), name='login'),       
    path('register/', register_view, name='register'),    
    path('home/', home_view, name='home'),                 
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]