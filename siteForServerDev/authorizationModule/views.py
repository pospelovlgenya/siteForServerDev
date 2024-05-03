from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .forms import UserRegisterForm, UserLoginForm
from .functions import check_token

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = user.get_token()
            login(request, user)
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
            token = user.get_token()
            if token == 'Error':
                return redirect('home')
            login(request, user)
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
    if (token_answer == 'Error'):
        signout(request)
    response = redirect('home')
    if (request.COOKIES.get('jwt_token') != token_answer):
        response.set_cookie('jwt_token', token_answer)
    return response
