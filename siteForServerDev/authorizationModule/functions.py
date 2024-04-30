import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError

from django.conf import settings 

from datetime import datetime, timedelta, UTC


def check_token(request):
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
        now_time = datetime.now(UTC) + timedelta(minutes=2)
        if (data['exp'] < int(now_time.timestamp())):
            token = request.user.refresh_token(token)

        return token
    except(ExpiredSignatureError):
        token = request.user.refresh_token(token)
        return token
    except(DecodeError):
        return 0