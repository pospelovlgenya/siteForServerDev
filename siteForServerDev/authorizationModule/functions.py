import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from django.conf import settings 

from datetime import datetime, timedelta, UTC


def check_token(request):
    """Проверка токена (его подписи и оставшегося времени жизни)"""
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
        # если токен существует, но id его пользователя и создателя не совпадает, то ошибка
        if (data['id'] != request.user.id):
            return 'Error'
        # если до истечения срока жизни токена меньше 2 минут, то он обновляется
        now_time = datetime.now(UTC) + timedelta(minutes=2)
        if (data['exp'] < int(now_time.timestamp())):
            token = request.user.refresh_token(token)
        # если после проверки ответ - это токен, то всё хорошо
        return token
    # если время жизни токена истекло, то производится попытка его обновления
    except(ExpiredSignatureError):
        token = request.user.refresh_token(token)
        return token
    # если токен изменили, то обновление не произойдёт
    except(DecodeError):
        return 'Error'
    

def decode_token(token):
    """Получение информации, содержащейся в токене"""
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