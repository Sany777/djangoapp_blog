from django.contrib import admin
from .models import *


admin.site.register(Topic)
admin.site.register(Entry)
admin.site.register(Banner)
admin.site.register(Bloger)
admin.site.register(Group)
admin.site.register(UserGroupPreference)