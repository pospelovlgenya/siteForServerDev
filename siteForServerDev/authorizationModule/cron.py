from datetime import datetime, timedelta, UTC

from django.conf import settings
from django_cron import CronJobBase, Schedule
from authorizationModule.models import BannedTokens, UpdatedTokens


class DeleteOldBannedTokens(CronJobBase):
    """Автоматическое удаление старых записей о заблокированных пользователях"""
    RUN_EVERY_MINS = settings.JWT_UPDATED_AUTODELETE_IN_MINS
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'authorizationModule.DeleteOldBannedTokens'

    def do(self):
        start_time = datetime.now(UTC) - timedelta(minutes=(settings.JWT_UPDATED_AUTODELETE_IN_MINS * 2))
        end_time = datetime.now(UTC)
        BannedTokens.objects.filter(created_at__range=(start_time, end_time)).delete()


class DeteleOldUpdatedTokens(CronJobBase):
    """Автоматическое удаление старых записей о недавно обновлённых токенах"""
    RUN_EVERY_MINS = settings.JWT_UPDATED_AUTODELETE_IN_MINS
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'authorizationModule.DeteleOldUpdatedTokens'

    def do(self):
        start_time = datetime.now(UTC) - timedelta(minutes=(settings.JWT_UPDATED_AUTODELETE_IN_MINS * 2))
        end_time = datetime.now(UTC)
        UpdatedTokens.objects.filter(created_at__range=(start_time, end_time)).delete()
