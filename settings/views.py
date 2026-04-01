from django.shortcuts import render
from .serializers import SettingsSerializer
from .models import Settings
from rest_framework.views import APIView
from rest_framework.response import Response

class SettingsView(APIView):
    def get(self, request):
        """
        Retrieve the current settings.
        """
        settings_instance = Settings.objects.get_or_create(id=1)[0]  # Assuming a single settings instance
        serializer = SettingsSerializer(settings_instance)
        return Response(serializer.data)
