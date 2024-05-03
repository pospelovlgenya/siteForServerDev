from django.contrib import admin
from .models import User, BannedTokens, UpdatedTokens

admin.site.register(User)
admin.site.register(BannedTokens)
admin.site.register(UpdatedTokens)