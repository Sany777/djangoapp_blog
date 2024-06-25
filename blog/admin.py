from django.contrib import admin
from .models import *

from django.contrib.sessions.models import Session

class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'session_data', 'expire_date']

admin.site.register(Session, SessionAdmin)

admin.site.register(Topic)
admin.site.register(Entry)
admin.site.register(Banner)
admin.site.register(FriendsGroup)
admin.site.register(ServiceContent)
admin.site.register(Rating)
admin.site.register(FriendCandidates)