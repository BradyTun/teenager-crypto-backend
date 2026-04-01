from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class VIPLevel(models.Model):
    level = models.IntegerField(unique=True, help_text="The VIP level (e.g., 1, 2, 3, etc.)")
    recharge_amount = models.FloatField(help_text="The amount required to recharge to reach this VIP level")
    claim_amount = models.FloatField(help_text="The amount available to claim for this VIP level")

    class Meta:
        ordering = ["level"]
        verbose_name = "VIP Level"
        verbose_name_plural = "VIP Levels"

    def __str__(self):
        return f"VIP {self.level}"


class UserVIP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vip_level = models.ForeignKey(VIPLevel, on_delete=models.CASCADE, null=True)
    has_claimed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'vip_level')  # Enforce uniqueness per user and VIP level

    def __str__(self):
        return f"{self.user.email} - VIP {self.vip_level.level if self.vip_level else 'None'}"


    def can_claim(self):
        """
        Checks if the user is eligible to claim their VIP reward.
        """
        total_balance = self.user.spot_balance + self.user.normal_balance + self.user.trading_balance
        if not self.has_claimed and self.vip_level and total_balance >= self.vip_level.recharge_amount:
            return True
        return False

    def claim_reward(self):
        """
        Claims the VIP reward if eligible.
        """
        if self.can_claim():

            # Mark as claimed
            self.has_claimed = True
            self.save()

            return True
        return False

    def __str__(self):
        return f"{self.user.email} - VIP {self.vip_level.level if self.vip_level else 'None'}"


class UserLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='link')
    linked_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='linked_to')

    def __str__(self):
        return f"{self.user.username} linked to {self.linked_user.username}"
    
    
class LoveRows(models.Model):
    amount_of_love = models.CharField(max_length=255)
    level_of_love = models.CharField(max_length=255)
    loves_reward = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.amount_of_love} - {self.level_of_love} - {self.loves_reward}"