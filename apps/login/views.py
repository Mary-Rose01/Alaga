from django.shortcuts import render
from django.contrib.auth.views import LoginView

class AlagaLoginView(LoginView):
    template_name = 'login/login.html'
    redirect_authenticated_user = True
# Create your views here.
