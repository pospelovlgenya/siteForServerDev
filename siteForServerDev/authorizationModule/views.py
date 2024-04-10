from django.shortcuts import render
from django.contrib.auth import login, logout
from .forms import *
# Create your views here.

def singup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # user.get_token()
            