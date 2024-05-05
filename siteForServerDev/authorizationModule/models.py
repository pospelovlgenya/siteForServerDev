import jwt
import random

from datetime import datetime, timedelta, UTC

from django.conf import settings 
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)


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

    # В качестве логина будет использоваться поле username
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

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
        UserTokens.delete_user_token(token)
        token = self.get_token()
        return token

    def get_token(self):
        """Позволяет пользователю получить новый токен"""
        if BannedTokens.is_user_in_table(self):
            return 'Error'
        return self.__generate_new_jwt_token__()
    
    def get_f2a_code(self):
        """
        Позволяет получить и привязать к пользователя код
        двухфакторки, также позволяет сменить этот код
        """
        code = self.__generate_new_f2a_code__()
        F2ACodes.new_f2a_code(code, self)
        return code
    
    def __generate_new_jwt_token__(self):
        """Создаёт новый jwt токен"""
        # Настройка времени истечения токена
        expire_date = (
            datetime.now(UTC) +
            settings.JWT_TOKEN_LIFETIME
        )

        token = jwt.encode(
            payload={
                "id": self.id,
                "username": self.username,
                "exp": expire_date,
                "is_staff": self.is_staff,
            },
            key=settings.SECRET_KEY,
            algorithm="HS256"
        )
        UserTokens.add_new_user_token(token, self, int(expire_date.timestamp()))
        return token 
    
    def __generate_new_f2a_code__(self):
        """Создаёт случайный код для двухфакторки"""
        code = random.randint(100000, 999999)
        return code


class UserTokens(models.Model):
    """Таблица активных токенов, которые используют пользователи"""
    token = models.CharField(primary_key=True, max_length=255)
    creator = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    expired_at = models.PositiveIntegerField(db_index=True)

    def add_new_user_token(token:str, user:User, expired_date:int):
        """Добавляет запись о новом токене пользователя"""
        UserTokens.objects.create(
            token = token,
            creator = user,
            expired_at = expired_date
        )
        return
    
    def is_user_have_free_slots(user:User):
        """проверяет наличие доступных мест под новый токен у пользователя"""
        num_of_user_sessions = UserTokens.objects.filter(creator = user).count()
        if (num_of_user_sessions < settings.NUMBER_OF_MAX_USER_ACTIVE_SESSIONS):
            return True
        return False
    
    def all_user_tokens(user_id):
        """Получение всех активных токенов пользователя"""
        user = User.objects.get(id=user_id)
        now_time = datetime.now(UTC)
        now_time = int(now_time.timestamp())
        tokens = UserTokens.objects.filter(Q(creator=user) & Q(expired_at__gt=now_time))
        return tokens

    def delete_user_token(token:str):
        """Удаляет один указанный токен"""
        if UserTokens.objects.filter(token=token).count():
            userToken = UserTokens.objects.get(token=token)
            UpdatedTokens.add_token_to_table(token, userToken.creator)
            userToken.delete()
        return

    def delete_all_user_tokens(token:str, user_id):
        """удаляет все токены, кроме используемого пользователем сейчас"""
        user = User.objects.get(id=user_id)
        userTokens = UserTokens.objects.filter(Q(creator=user) & ~Q(token=token))
        for userToken in userTokens:
            UpdatedTokens.add_token_to_table(userToken.token, userToken.creator)
        userTokens.delete()
        return

    def delete_old():
        """Удаление старых записей"""
        now_time = datetime.now(UTC)
        now_time = int(now_time.timestamp())
        UserTokens.objects.filter(expired_at__lt=now_time).delete()
        return


class F2ACodes(models.Model):
    """Таблица созданных кодов двухфакторки"""
    creator = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    code = models.PositiveIntegerField(db_index=True, unique=True)
    created_at = models.DateTimeField(auto_now=True)

    def new_f2a_code(code:int, user:User):
        """Добавляет или обновляет код двухфакторки пользователя"""
        F2ACodes.objects.update_or_create(creator=user, defaults={'code':code})
        return

    def check_f2a_code(code:int, user:User):
        """Проверка введённого кода двухфакторки на существование и верность"""
        now_time = datetime.now(UTC) - settings.TWO_FACTOR_CODE_LIFETIME
        if (F2ACodes.objects.filter(Q(creator=user) & Q(created_at__gt=now_time)).count()):
            if (F2ACodes.objects.get(creator=user).code == code):
                return True
        return False
    
    def delete_old():
        """Удаление старых записей"""
        now_time = datetime.now(UTC) - timedelta(minutes=settings.OLD_AUTODELETE_IN_MINS)
        F2ACodes.objects.filter(created_at__lt=now_time).delete()
        return


class UpdatedTokens(models.Model):
    """Таблица недавно обновлёных токенов"""
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_token_in_table(token:str, user:User):
        """Проверка токена в таблице недавно обновлённых и добавление пользователя в бан при положительном ответе"""
        if (UpdatedTokens.objects.filter(token=token).count()):
            BannedTokens.objects.create(
            token = token,
            creator = user
            )
            return True
        return False
    
    def add_token_to_table(token:str, user:User):
        """Добавление старого токена в таблицу недавно обновлённых"""
        UpdatedTokens.objects.create(
            token = token,
            creator = user
            )
        return
    
    def delete_old():
        """Удаление старых записей"""
        now_time = datetime.now(UTC) - timedelta(minutes=settings.OLD_AUTODELETE_IN_MINS)
        UpdatedTokens.objects.filter(created_at__lt=now_time).delete()
        return


class BannedTokens(models.Model):
    """Таблица заблокированных пользователей (обновивших один токен дважды)"""
    token = models.CharField(db_index=True, max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_user_in_table(user:User):
        """Проверка пользователя в таблице банов"""
        if (BannedTokens.objects.filter(creator=user).count()):
            return True
        return False

    def delete_old():
        """Удаление старых записей"""
        now_time = datetime.now(UTC) - timedelta(minutes=settings.OLD_AUTODELETE_IN_MINS)
        BannedTokens.objects.filter(created_at__lt=now_time).delete()
        return
    