from django.db import models

class Settings(models.Model):
    invitation_code_required = models.BooleanField(default=True)
    otp_required = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Settings"