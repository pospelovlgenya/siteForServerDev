import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from django.conf import settings 

from datetime import datetime, timedelta, UTC

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
