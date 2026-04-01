from django.urls import path
from .views import ContactInfoAPI

urlpatterns = [
    path('', ContactInfoAPI.as_view(), name='contact-info-api'),
]
