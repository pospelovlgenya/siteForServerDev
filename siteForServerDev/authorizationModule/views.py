from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .forms import *
from .functions import check_token, decode_token

def home(request):
    token_data = decode_token(request.COOKIES.get('jwt_token'))
    return render(request, "authorizationModule/home.html", {'token_data': token_data})

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
    response = redirect('home')
    response.delete_cookie('jwt_token')
    return response

@login_required
def refreshtoken(request):
    token_answer = check_token(request)
    if (token_answer == 0):
        signout(request)
    response = redirect('home')
    if (request.COOKIES.get('jwt_token') != token_answer):
        response.set_cookie('jwt_token', token_answer)
    return response
