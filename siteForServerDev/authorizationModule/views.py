from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .models import F2ACodes, UserTokens
from .forms import UserRegisterForm, UserLoginForm, F2aForm
from .functions import check_token, decode_token


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
    chit = ''
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
    # проверка оставшихся у пользователя доступных токенов доступа
    if UserTokens.is_user_have_free_slots(request.user):
        """ chit используется только для упрощения введения кода 
         (может быть изменён на любой другой способ получения кода
         пользователем без приложения значительных усилий) """
        chit = request.user.get_f2a_code()
    else:
        return redirect('tooMany')
    return render(request, 'authorizationModule/f2a.html', {'form': form, 'chit':chit})

@login_required
def too_many(request):
    """Используется для решения проблемы использования пользователем всех
      доступных токенов доступа (заставляет отключить все остальные токены)"""
    if UserTokens.is_user_have_free_slots(request.user):
        return redirect('f2a')
    return render(request, 'authorizationModule/toomany.html')

def signout(request):
    """Полноценный выход из всего приложения"""
    token = request.COOKIES.get('jwt_token')
    UserTokens.delete_user_token(token)
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

def delete_token(request, token):
    """Управляет удалением токенов"""
    if token == 'toomany':
        UserTokens.delete_all_user_tokens(' ', request.user.id)
        return redirect('f2a')
    if token == 'all':
        now_token = request.COOKIES.get('jwt_token')
        data = decode_token(now_token)
        UserTokens.delete_all_user_tokens(now_token, data['id'])
    else:
        UserTokens.delete_user_token(token)
    return redirect('home')
