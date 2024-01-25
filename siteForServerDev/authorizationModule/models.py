import jwt

from datetime import datetime, timedelta
from django.conf import settings 
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, password='ChangeMe1'):
        """ Создает и возвращает пользователя с почтой, паролем и именем. """
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # Время создания пользователя
    created_at = models.DateTimeField(auto_now_add=True)
    # Время последнего обновления объекта
    updated_at = models.DateTimeField(auto_now=True)

    # В качестве логина будет использоваться поле email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Указывает управляющего объектами класса
    objects = UserManager()

    def __str__(self):
        return self.email
    
    @property
    def create_token(self):
        # Сокращает команду для генерации токена
        return self._generate_jwt_token()
    
    # Необходим, так как у пользователя нет имени и фамилии
    def get_full_name(self):
        return self.username
    
    # Необходим, так как у пользователя нет имени и фамилии
    def get_short_name(self):
        return self.username
    
    # Генератор jwt токена
    def _generate_jwt_token(self):
        expire_date = ( datetime.now() +
        # Настройка времени истечения токена
        timedelta(weeks=0, days=0, hours=0, minutes=10, seconds=0)
        )

        token = jwt.encode(
            payload={
                'id':self.pk,
                'exp':int(expire_date.strftime('%s'))
            },
            key=settings.SECRET_KEY,
            algorithm='HS256'
        )

        return token.decode('utf-8')

