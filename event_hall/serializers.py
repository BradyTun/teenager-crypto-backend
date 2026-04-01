from rest_framework import serializers
from .models import VIPLevel, LoveRows


class VIPLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VIPLevel
        fields = ["id", "level", "recharge_amount", "claim_amount"]

class LoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoveRows
        fields = ["amount_of_love", "level_of_love", "loves_reward"]