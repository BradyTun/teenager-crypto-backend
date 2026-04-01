from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Trade, Duration
from .serializers import TradeSerializer, TradeHistorySerializer, DurationSerializer
from django.utils.timezone import now


class OpenTradeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=TradeSerializer,
        responses={201: "Trade opened successfully", 400: "Invalid data"},
    )
    def post(self, request):
        user = request.user
        serializer = TradeSerializer(data=request.data, context={"request": request})
        
        # Check if the serializer data is valid
        if serializer.is_valid():
            trade_amount = serializer.validated_data.get("amount")
            
            # Check if the user has sufficient balance
            if user.trading_balance < trade_amount:
                return Response(
                    {"error": "Insufficient trading balance."},
                    status=400
                )
            
            # Deduct the trade amount from the user's balance
            user.trading_balance -= trade_amount
            user.save()  # Save the updated balance

            # Save the trade with the user associated
            serializer.save(user=user)
            
            return Response({"message": "Trade opened successfully"}, status=201)
        
        # If data is invalid, return errors
        return Response(serializer.errors, status=400)


class CloseTradeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Close a trade if its duration has passed.",
        responses={200: "Trade closed successfully", 404: "Trade not found or already closed"},
    )
    def post(self, request, trade_id):
        try:
            trade = Trade.objects.get(id=trade_id, user=request.user, is_closed=False)
            if now() >= trade.opened_at + trade.duration.duration:
                trade.is_closed = True
                trade.save()
                user = trade.user
                if trade.profit_or_loss > 0:
                    user.trading_balance += trade.amount + trade.profit_or_loss
                user.save()
                return Response({"message": "Trade closed successfully"}, status=200)
            return Response({"message": "Trade duration has not passed yet"}, status=400)
        except Trade.DoesNotExist:
            return Response({"message": "Trade not found or already closed"}, status=404)


class TradeHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TradeHistorySerializer

    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user).order_by("-opened_at")[:20]


class DurationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DurationSerializer
    queryset = Duration.objects.all()
