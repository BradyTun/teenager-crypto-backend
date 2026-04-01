from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone

from .managers import CustomUserManager

import random
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    MODE_CHOICES = [
        ("always_win", "Always Win"),
        ("always_lose", "Always Lose"),
        ("luck", "Luck"),
    ]

    user_id = models.CharField(max_length=20, unique=True)
    referred_user = models.ForeignKey(
        "self",  # References the same User model
        on_delete=models.SET_NULL,  # Set to null if the referred user is deleted
        null=True,
        blank=True,
        related_name="referrals",  # Allows reverse lookup for referred users
    )
    last_login_ip = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        help_text=_("IP address of the last login"),
    )
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    username = models.CharField(max_length=1024, null=False, unique=False)
    photo = models.ImageField(
        upload_to="profile_photo/", default="profile_photo/default.png"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=1024)
    spot_balance = models.FloatField(default=0)
    normal_balance = models.FloatField(default=0)
    trading_balance = models.FloatField(default=0)
    closed_withdrawal = models.BooleanField(default=False)
    closed_trading = models.BooleanField(default=False)
    vip_level = models.IntegerField(default=0)
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default="luck",  # Default mode is "luck"
        help_text=_("Determines the user's luck mode: always wins, always loses, or based on luck."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    fcm_registration_token = models.CharField(max_length=255, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.user_id:
            while True:
                new_id = "USER_" + "".join(
                    [str(random.randint(0, 9)) for _ in range(6)]
                )
                if not User.objects.filter(user_id=new_id).exists():
                    self.user_id = new_id
                    break
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.user_id} - Mode: {self.get_mode_display()}"  # Human-readable mode


class OTP(models.Model):
    email = models.EmailField(null=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp", null=True)
    token = models.CharField(max_length=6, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_minutes = models.IntegerField(default=10)

    def get_token(self):
        token = str(random.randint(100000, 999999))
        self.token = token
        self.save()
        return self.token

    def verify(self, token: str):
        if self.token and self.token == token:
            if timezone.now() - self.updated_at < datetime.timedelta(minutes=self.expiry_minutes):
                self.token = None
                self.save()
                return True
        return False
