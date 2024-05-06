from datetime import datetime, timedelta, UTC

from django.conf import settings
from django_cron import CronJobBase, Schedule
from authorizationModule.models import BannedTokens, UpdatedTokens, F2ACodes, UserTokens


class DeleteOldBannedTokens(CronJobBase):
    """Автоматическое удаление старых записей о заблокированных токенах и пользователях"""
    RUN_EVERY_MINS = settings.CRONS_PERIOD_IN_MINS
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'authorizationModule.DeleteOldBannedTokens'

    def do(self):
        BannedTokens.delete_old()


class DeteleOldUpdatedTokens(CronJobBase):
    """Автоматическое удаление старых записей о недавно обновлённых токенах"""
    RUN_EVERY_MINS = settings.CRONS_PERIOD_IN_MINS
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'authorizationModule.DeteleOldUpdatedTokens'

    def do(self):
        UpdatedTokens.delete_old()

class DeleteOldF2ACodes(CronJobBase):
    """Автоматическое удаление старых записей о кодах двухфакторки"""
    RUN_EVERY_MINS = settings.CRONS_PERIOD_IN_MINS
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'authorizationModule.DeleteOldF2ACodes'

    def do(self):
        F2ACodes.delete_old()


class DeleteOldUserTokens(CronJobBase):
    """Автоматическое удаление старых записей о токенах пользователей"""
    RUN_EVERY_MINS = settings.CRONS_PERIOD_IN_MINS
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'authorizationModule.DeleteOldUserTokens'

    def do(self):
        UserTokens.delete_old()
