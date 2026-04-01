from .views import SettingsView
from django.urls import path

urlpatterns = [
    path("", SettingsView.as_view(), name="settings"),
]