from django.contrib import admin
from .models import User, BannedTokens, UpdatedTokens, F2ACodes, UserTokens

admin.site.register(User)
admin.site.register(BannedTokens)
admin.site.register(UpdatedTokens)
admin.site.register(F2ACodes)
admin.site.register(UserTokens)
