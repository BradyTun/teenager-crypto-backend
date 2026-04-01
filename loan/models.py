from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.db import models, transaction


class LoanableCoin(models.Model):
    name = models.CharField(max_length=50)
    pic = models.ImageField(upload_to="loanable_coins/")
    network = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.network})"


class Loan(models.Model):
    LOAN_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.ForeignKey(LoanableCoin, on_delete=models.CASCADE)
    amount = models.FloatField()
    nrc_front_pic = models.ImageField(upload_to="loan_nrc/")
    nrc_back_pic = models.ImageField(upload_to="loan_nrc/")
    loan_terms = models.IntegerField(help_text="Loan duration in days")
    total_interest = models.FloatField()
    repayment_amount = models.FloatField()
    account_type = models.CharField(
        max_length=50, choices=[("Spot", "Spot"), ("Normal", "Normal"), ("Trading", "Trading")]
    )
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default="Pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan - {self.user.email} - {self.amount} {self.coin.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Check if the status has changed to "Approved"
        if self.pk:
            # Fetch the previous instance from the database
            previous_instance = Loan.objects.get(pk=self.pk)
            if previous_instance.status != "Approved" and self.status == "Approved":
                with transaction.atomic():
                    # Increase user's trading balance
                    if self.account_type == 'Trading':
                        self.user.trading_balance += self.amount
                    elif self.account_type == 'Normal':
                        self.user.normal_balance += self.amount
                    else:
                        self.user.spot_balance += self.amount
                    self.user.save()

        super().save(*args, **kwargs)