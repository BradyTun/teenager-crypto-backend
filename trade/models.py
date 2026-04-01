from django.db import models
from django.conf import settings
from datetime import timedelta
import random


class Duration(models.Model):
    duration = models.DurationField(help_text="Duration of the trade (timedelta object)")
    win_percentage = models.FloatField(help_text="Win percentage for this duration (e.g., 10.0 for 10%)")

    def __str__(self):
        return f"{self.duration} - {self.win_percentage}%"


class Trade(models.Model):
    TRADE_METHOD_CHOICES = [
        ("Buy Up", "Buy Up"),
        ("Buy Down", "Buy Down"),
    ]
    
    coin = models.CharField(max_length=1024)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades")
    trade_method = models.CharField(max_length=20, choices=TRADE_METHOD_CHOICES)
    amount = models.FloatField()
    duration = models.ForeignKey(Duration, on_delete=models.CASCADE)
    opened_at = models.DateTimeField(auto_now_add=True)
    open_price = models.FloatField(null=True)
    close_price = models.FloatField(null=True)
    profit_or_loss = models.FloatField(null=True, blank=True, help_text="Profit or loss amount (set when trade is created)")
    is_closed = models.BooleanField(default=False, help_text="True if the trade is closed")

    def __str__(self):
        return f"Trade {self.pk} - {self.user.email} - {self.trade_method} - {self.amount} - Closed: {self.is_closed}"
