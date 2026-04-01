from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Coin(models.Model):
    name = models.CharField(max_length=50)
    market_price = models.FloatField(null=True)
    network = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to="coin_qr_codes/")

    def __str__(self):
        return f"{self.name} ({self.network})"


class TransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("Deposit", "Deposit"),
        ("Withdrawal", "Withdrawal"),
        ("Internal", "Internal"),
    ]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.FloatField()
    currency = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    network = models.CharField(max_length=50, null=True, blank=True)
    tx_id = models.CharField(max_length=255, null=True, blank=True)
    account_from = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Spot", "Trading", "Normal"
    account_to = models.CharField(max_length=50, null=True, blank=True)  # Used for Internal transactions
    timestamp = models.DateTimeField(auto_now_add=True)
    withdrawal_address = models.CharField(max_length=50, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.user.email} - {self.amount} {self.currency}"


class Deposit(models.Model):
    transaction_history = models.OneToOneField(TransactionHistory, null=True, blank=True, related_name='deposit', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50, choices=[("Spot", "Spot"), ("Trading", "Trading"), ("Normal", "Normal")])
    amount = models.FloatField()
    payment_screenshot = models.ImageField(upload_to="deposits/")
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Confirmed", "Confirmed"), ("Rejected", "Rejected")], default="Pending")
    timestamp = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        is_update = self.pk is not None  # Check if this is an update

        if is_update:  # On update
            original_status = Deposit.objects.get(pk=self.pk).status
            if original_status != "Confirmed" and self.status == "Confirmed":
                balance_field = f"{self.account_type.lower()}_balance"
                setattr(self.user, balance_field, getattr(self.user, balance_field) + self.amount)
                self.user.save()

            # Update related TransactionHistory
            self.transaction_history.status = self.status
            self.transaction_history.save()

        else:  # On creation
            super().save(*args, **kwargs)  # Save once to generate pk
            transaction_history = TransactionHistory.objects.create(
                user=self.user,
                transaction_type="Deposit",
                amount=self.amount,
                currency=self.coin.name,
                status=self.status,
                network=self.coin.network,
                timestamp=now(),
            )
            self.transaction_history = transaction_history
            super().save(update_fields=["transaction_history"]) 

        if is_update:  # Save again for updates only after handling logic
            super().save(*args, **kwargs)
            
    def delete(self, *args, **kwargs):
        # Delete the related TransactionHistory
        if self.transaction_history:
            self.transaction_history.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Deposit - {self.user.email} - {self.amount}"



class Withdrawal(models.Model):
    transaction_history = models.OneToOneField(TransactionHistory, null=True, blank=True, related_name='withdrawal', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50, choices=[("Spot", "Spot"), ("Trading", "Trading"), ("Normal", "Normal")])
    amount = models.FloatField()
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Confirmed", "Confirmed"), ("Rejected", "Rejected")], default="Pending")
    timestamp = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    note = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_update = self.pk is not None  # Check if this is an update

        if is_update:  # On update
            original_status = Withdrawal.objects.get(pk=self.pk).status
            if original_status != "Rejected" and self.status == "Rejected":
                balance_field = f"{self.account_type.lower()}_balance"
                setattr(self.user, balance_field, getattr(self.user, balance_field) + self.amount)
                self.user.save()

            # Update related TransactionHistory
            self.transaction_history.status = self.status
            self.transaction_history.note = self.note
            self.transaction_history.save()
            
            super().save(*args, **kwargs)


        else:  # On creation
            balance_field = f"{self.account_type.lower()}_balance"
            total_amount = self.amount # Deduct 1% fee
            if getattr(self.user, balance_field) < total_amount:
                raise ValueError("Insufficient balance")
            setattr(self.user, balance_field, getattr(self.user, balance_field) - total_amount)
            self.user.save()
            
            super().save(*args, **kwargs)

            # Log to transaction history
            transaction_history = TransactionHistory.objects.create(
                user=self.user,
                transaction_type="Withdrawal",
                amount=self.amount,
                currency=self.coin.name,
                status="Pending",
                network=self.coin.network,
                timestamp=now(),
                withdrawal_address=self.address
            )
            
            self.transaction_history = transaction_history
            super().save(update_fields=["transaction_history"]) 
        
    def delete(self, *args, **kwargs):
        # Delete the related TransactionHistory
        if self.transaction_history:
            self.transaction_history.delete()
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"Withdrawal - {self.user.email} - {self.amount}"


class InternalTransfer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_from = models.CharField(max_length=50, choices=[("Spot", "Spot"), ("Trading", "Trading"), ("Normal", "Normal")])
    account_to = models.CharField(max_length=50, choices=[("Spot", "Spot"), ("Trading", "Trading"), ("Normal", "Normal")])
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_update = self.pk is not None  # Check if this is an update

        if is_update:  # On update
            # Update related TransactionHistory
            transaction = TransactionHistory.objects.filter(
                user=self.user,
                transaction_type="Internal",
                amount=float(self.amount),
                account_from=self.account_from,
                account_to=self.account_to,
            ).first()
            if transaction:
                transaction.save()

        else:  # On creation
            from_balance_field = f"{self.account_from.lower()}_balance"
            to_balance_field = f"{self.account_to.lower()}_balance"

            if getattr(self.user, from_balance_field) < float(self.amount):
                raise ValueError("Insufficient balance")

            # Update balances
            setattr(self.user, from_balance_field, getattr(self.user, from_balance_field) - float(self.amount))
            setattr(self.user, to_balance_field, getattr(self.user, to_balance_field) + float(self.amount))
            self.user.save()

            # Log to transaction history
            TransactionHistory.objects.create(
                user=self.user,
                transaction_type="Internal",
                amount=float(self.amount),
                currency="USD",
                status="Success",
                account_from=self.account_from,
                account_to=self.account_to,
                timestamp=now(),
            )
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Internal Transfer - {self.user.email} - {self.amount}"
