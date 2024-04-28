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
    
    # позволяет пользователю получить новый токен
    def get_token(self):
        return self.__generate_new_jwt_token__()
    
    # Необходим, так как у пользователя нет имени и фамилии
    def get_full_name(self):
        return self.username
    
    # Необходим, так как у пользователя нет имени и фамилии
    def get_short_name(self):
        return self.username

    # для сохранения нового токена в бд
    # def __save_token_to_bd__(self, token:str):
    #     TokenForUser.objects.create(token=token, creator=self)

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

        # self.__save_token_to_bd__(token)
        return token
    # jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"])


# class TokenForUser(models.Model):
#     token = models.CharField(db_index=True, max_length=255)
#     creator = models.ForeignKey(User, on_delete=models.CASCADE)
#     is_banned = models.BooleanField(default=False)
#     is_updated = models.BooleanField(default=False)
#     updated_at = models.DateTimeField(auto_now=True)

#     # метод для блокировки всех токенов пользователя
#     def ban_all_user_tokens(token_for_ban:str):
#         user_for_ban = TokenForUser.objects.filter(token=token_for_ban).first().creator
#         TokenForUser.objects.filter(creator=user_for_ban).update(is_banned=True)


class UpdatedTokens(models.Model):
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)


class BannedTokens(models.Model):
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
