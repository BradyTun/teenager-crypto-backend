from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Coin, Deposit, Withdrawal, InternalTransfer, TransactionHistory
from .serializers import *
from .notification import *
from rest_framework import status


class UnnotifiedTransactionsView(APIView):
    def get(self, request):
        # Fetch unnotified deposits and withdrawals
        unnotified_deposits = Deposit.objects.filter(notified=False)
        unnotified_withdrawals = Withdrawal.objects.filter(notified=False)

        # Serialize data
        deposits_data = DepositNotiSerializer(unnotified_deposits, many=True).data
        withdrawals_data = WithdrawalNotiSerializer(unnotified_withdrawals, many=True).data

        # Update notified status to True for all unnotified deposits and withdrawals
        unnotified_deposits.update(notified=True)
        unnotified_withdrawals.update(notified=True)

        return Response(
            {
                "deposits": deposits_data,
                "withdrawals": withdrawals_data,
            },
            status=status.HTTP_200_OK,
        )
        
class AvailableCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Fetch available coins for deposit",
        responses={200: CoinSerializer(many=True)},
    )
    def get(self, request):
        coins = Coin.objects.all()
        serializer = CoinSerializer(coins, many=True)
        return Response(serializer.data)


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a deposit request",
        request_body=DepositSerializer,
        responses={201: DepositSerializer},
    )
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            deposit = serializer.save(user=request.user)

            # Notify superusers
            admin_url = f"/admin/transactions/deposit/{deposit.id}/change/"
            send_notification_to_superusers(
                title=f"New Deposit Request: {deposit.id}",
                body=f"User {request.user.username} has requested a deposit of ${deposit.amount}.",
                admin_url=admin_url,
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a withdrawal request",
        request_body=WithdrawalSerializer,
        responses={201: WithdrawalSerializer},
    )
    def post(self, request):
        # Check if user has withdrawals closed
        if request.user.closed_withdrawal:
            return Response(
                {"detail": "You can't withdraw at that moment and please contact to customer service."},
                status=403
            )
            
        if Withdrawal.objects.filter(user=request.user, status='Pending').exists():
            return Response(
                {"detail": "You already have a pending withdrawal."},
                status=403
            )


        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            withdrawal = serializer.save(user=request.user)

            # Notify superusers
            admin_url = f"/admin/transactions/withdrawal/{withdrawal.id}/change/"
            send_notification_to_superusers(
                title=f"New Withdrawal Request : {withdrawal.id}",
                body=f"User {request.user.username} has requested a withdrawal of ${withdrawal.amount}.",
                admin_url=admin_url,
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class InternalTransferView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Transfer funds between account balances",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "account_from": openapi.Schema(type=openapi.TYPE_STRING),
                "account_to": openapi.Schema(type=openapi.TYPE_STRING),
                "amount": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        ),
        responses={201: "Transfer Successful"},
    )
    def post(self, request):
        data = request.data
        try:
            transfer = InternalTransfer.objects.create(
                user=request.user,
                account_from=data["account_from"],
                account_to=data["account_to"],
                amount=data["amount"],
            )
            return Response({"message": "Transfer Successful"}, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Fetch transaction history",
        responses={200: TransactionHistorySerializer(many=True)},
    )
    def get(self, request):
        history = TransactionHistory.objects.filter(
            user=request.user).order_by("-timestamp")
        serializer = TransactionHistorySerializer(history, many=True)
        return Response(serializer.data)
