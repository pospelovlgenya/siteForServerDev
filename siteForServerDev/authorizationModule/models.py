import jwt
import random

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
    """Таблица пользователей"""
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # Время создания пользователя
    created_at = models.DateTimeField(auto_now_add=True)
    # Время последнего обновления объекта "пользователь"
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

    def refresh_token(self, token):
        """Проверяет токен на доступность обновления и обновляет"""
        if BannedTokens.is_user_in_table(self):
            return 'Error'
        if UpdatedTokens.is_token_in_table(token, self):
            return 'Error'
        UpdatedTokens.add_token_to_table(token, self)
        token = self.get_token()
        return token

    def get_token(self):
        """Позволяет пользователю получить новый токен"""
        if BannedTokens.is_user_in_table(self):
            return 'Error'
        return self.__generate_new_jwt_token__()
    
    def __generate_new_jwt_token__(self):
        """Создаёт новый jwt токен"""
        expire_date = (
            # Настройка времени истечения токена
            datetime.now(UTC) +
            settings.JWT_TOKEN_LIFETIME
        )

        token = jwt.encode(
            payload={
                "id": self.id,
                "exp": expire_date,
                "nbf": datetime.now(UTC),
                "is_staff": self.is_staff,
            },
            key=settings.SECRET_KEY,
            algorithm="HS256"
        )
        return token 
    
    def __generate_new_f2a_code__(self):
        """Создаёт случайный код для двухфакторки"""
        code = random.randint(100000, 999999)
        return code


class F2ACodes(models.Model):
    """Таблица созданных кодов двухфакторки"""
    code = models.IntegerField(db_index=True, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class UpdatedTokens(models.Model):
    """Таблица недавно обновлёных токенов"""
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_token_in_table(token, user):
        """Проверка токена в таблице недавно обновлённых и добавление пользователя в бан при положительном ответе"""
        if (UpdatedTokens.objects.filter(token=token).count()):
            BannedTokens.objects.create(
            token = token,
            creator = user
            )
            return True
        return False
    
    def add_token_to_table(token, user):
        """Добавление старого токена в таблицу недавно обновлённых"""
        UpdatedTokens.objects.create(
            token = token,
            creator = user
            )
        return


class BannedTokens(models.Model):
    """Таблица заблокированных пользователей (обновивших токен дважды)"""
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_user_in_table(user):
        """Проверка пользователя в таблице банов"""
        if (BannedTokens.objects.filter(creator=user).count()):
            return True
        return False
