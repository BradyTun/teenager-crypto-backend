from django.db import models

class ContactInfo(models.Model):
    # user_email = models.EmailField(unique=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
