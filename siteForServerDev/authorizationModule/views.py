from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import *

# Create your views here.


def home(request):
    return render(request, "authorizationModule/home.html")

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            token = user.get_token()
            response = redirect('home')
            response.set_cookie('jwt_token', token)
            return response
    else:
        form = UserRegisterForm()
    return render(request, 'authorizationModule/signup.html', {'form': form})

def signin(request):
    if request.method =='POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            token = user.get_token()
            response = redirect('home')
            response.set_cookie('jwt_token', token)
            return response
    else:
        form = UserLoginForm()
    return render(request, 'authorizationModule/signin.html', {'form': form})

@login_required
def signout(request):
    logout(request)
    return redirect('home')