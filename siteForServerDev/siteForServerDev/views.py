from django.shortcuts import render
from authorizationModule.functions import decode_token
from authorizationModule.models import UserTokens


def home(request):
    user_tokens = 0
    token_data = decode_token(request.COOKIES.get('jwt_token'))
    if token_data != 'Error':
        user_tokens = UserTokens.all_user_tokens(token_data['id'])
    return render(request, "siteForServerDev/home.html", {'token_data': token_data, 'user_tokens':user_tokens})
