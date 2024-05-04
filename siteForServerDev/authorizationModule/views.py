from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .models import F2ACodes
from .forms import UserRegisterForm, UserLoginForm, F2aForm
from .functions import check_token


def signup(request):
    """Регистрация"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            response = redirect('f2a')
            return response
    else:
        form = UserRegisterForm()
    return render(request, 'authorizationModule/signup.html', {'form': form})

def signin(request):
    """Авторизация"""
    if request.method =='POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = redirect('f2a')
            return response
    else:
        form = UserLoginForm()
    return render(request, 'authorizationModule/signin.html', {'form': form})

@login_required
def f2a_check(request):
    """Проверка кода двухфакторки"""
    if request.method =='POST':
        form = F2aForm(data=request.POST)
        if form.is_valid():
            if F2ACodes.check_f2a_code(int(form.cleaned_data.get('code')), request.user):
                token = request.user.get_token()
                if token == 'Error':
                    return redirect('home')
                response = redirect('home')
                response.set_cookie('jwt_token', token)
                logout(request)
                return response
    else:
        form = F2aForm()
    chit = request.user.get_f2a_code()
    return render(request, 'authorizationModule/f2a.html', {'form': form, 'chit':chit})

def signout(request):
    """Полноценный выход из всего приложения"""
    response = redirect('home')
    response.delete_cookie('jwt_token')
    return response

def refreshtoken(request):
    """Проверка подлиности токена и его обновление при необходимости"""
    token_answer = check_token(request)
    response = redirect('home')
    if (request.COOKIES.get('jwt_token') != token_answer):
        response.set_cookie('jwt_token', token_answer)
    return response
