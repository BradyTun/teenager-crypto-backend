from django.contrib import admin
from .models import Settings

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Settings._meta.fields]
    list_editable = [field.name for field in Settings._meta.fields if field.name != 'id']