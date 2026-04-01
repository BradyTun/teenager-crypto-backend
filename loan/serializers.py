from rest_framework import serializers
from .models import LoanableCoin, Loan


class LoanableCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanableCoin
        fields = ["id", "name", "pic", "network"]


class LoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "coin",
            "amount",
            "nrc_front_pic",
            "nrc_back_pic",
            "loan_terms",
            "total_interest",
            "repayment_amount",
            "account_type",
        ]

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return data


class LoanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "coin",
            "amount",
            "loan_terms",
            "total_interest",
            "repayment_amount",
            "status",
            "timestamp",
        ]
