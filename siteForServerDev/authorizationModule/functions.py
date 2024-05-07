import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from datetime import datetime, timedelta, UTC
import requests
from bs4 import BeautifulSoup

from django.conf import settings 

from .models import User


def check_token(request):
    """
    Проверка токена (его подписи и оставшегося времени жизни), 
    если ответом является токен, то проверка пройдена
    """
    token = request.COOKIES.get('jwt_token')
    try:
        data = jwt.decode(
            jwt=token, 
            key=settings.SECRET_KEY,
            algorithms="HS256",
            options={
                'verify_signature': True
                },
            )
        # если до истечения срока жизни токена меньше 2 минут, то он обновляется
        now_time = datetime.now(UTC) + timedelta(minutes=2)
        if (data['exp'] < int(now_time.timestamp())):
            token = User.objects.get(id=data['id']).refresh_token(token)
        return token
    # если время жизни токена истекло, то производится попытка его обновления
    except(ExpiredSignatureError):
        data = decode_token(token)
        token = User.objects.get(id=data['id']).refresh_token(token)
        return token
    # если токен изменили, то обновление не произойдёт
    except(DecodeError):
        return 'Error'
    

def decode_token(token):
    """Получение информации, содержащейся в токене (без проверок)"""
    try:
        data = jwt.decode(
            jwt=token, 
            key=settings.SECRET_KEY,
            algorithms="HS256",
            options={
                'verify_signature': False
                },
            )
        return data
    # любая ошибка будет возвращена в виде 'Error'
    except(InvalidTokenError):
        return 'Error'

def get_weather_info(city='khanty-mansiysk'):
    """Получает погоду города"""
    url = f"https://yandex.ru/pogoda/{city}"
    url_response = requests.get(url)
    temperature = 'Error'
    wind_speed = 'Error'
    if url_response.status_code != 200:
        return temperature, str(url_response.status_code)
    page = BeautifulSoup(url_response.content, 'html.parser')
    weather_block = page.find('div', class_='fact')
    if weather_block is None:
        return temperature, 'Maybe Yandex was ban us'
    temperature = weather_block.find('span', class_='temp__value').text
    wind_speed = weather_block.find('span', class_='wind-speed').text
    return temperature, wind_speed
