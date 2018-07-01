from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import CustomUser, OfficeSpace


@admin.register(OfficeSpace)
class OfficeSpaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')
