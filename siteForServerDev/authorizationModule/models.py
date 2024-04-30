import jwt

from datetime import datetime, UTC
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
    
    # Необходим, так как у пользователя нет имени и фамилии
    def get_full_name(self):
        return self.username
    
    # Необходим, так как у пользователя нет имени и фамилии
    def get_short_name(self):
        return self.username
    
    # позволяет пользователю получить новый токен
    def get_token(self):
        if (BannedTokens.objects.filter(creator=self).count()):
            return 'you in ban list'
        return self.__generate_new_jwt_token__()
    
    # проверяет токен и обновляет
    def refresh_token(self, token):
        # проверка пользователя в таблице банов
        if (BannedTokens.objects.filter(creator=self).count()):
            return 'you in ban list'
        # проверка токена в таблице недавно обновлённых
        if (UpdatedTokens.objects.filter(token=token).count()):
            BannedTokens.objects.create(
            token = token,
            creator = self
            )
            return 'you steal token'
        # добавление старого токена в таблицу недавно обновлённых
        UpdatedTokens.objects.create(
            token = token,
            creator = self
            )
        # создание нового токена
        token = self.get_token()
        return token

    # создаёт новый токен и сохраняет в бд токенов
    def __generate_new_jwt_token__(self):
        expire_date = (
            datetime.now(UTC) +
            # Настройка времени истечения токена
            settings.JWT_TOKEN_LIFETIME
        )

        token = jwt.encode(
            payload={
                "exp": expire_date,
                "nbf": datetime.now(UTC),
                "is_staff": self.is_staff,
            },
            key=settings.SECRET_KEY,
            algorithm="HS256"
        )
        return token


class UpdatedTokens(models.Model):
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)


class BannedTokens(models.Model):
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
