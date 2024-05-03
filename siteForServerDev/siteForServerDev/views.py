from django.shortcuts import render
from authorizationModule.functions import decode_token

def home(request):
    token_data = decode_token(request.COOKIES.get('jwt_token'))
    return render(request, "siteForServerDev/home.html", {'token_data': token_data})