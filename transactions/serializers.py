from rest_framework import serializers
from .models import Coin, Deposit, Withdrawal, TransactionHistory

class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ["id", "name", "network", "address", "qr_code", "market_price"]

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ["id", "coin", "account_type", "amount", "payment_screenshot", "status", "timestamp"]

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ["id", "coin", "account_type", "amount", "address", "status", "timestamp"]
        
class DepositNotiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = "__all__"

class WithdrawalNotiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = "__all__"

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = ["transaction_type", "amount", "currency", "status", "network", "timestamp", "tx_id", "account_to", "account_from", "withdrawal_address", "note"]
