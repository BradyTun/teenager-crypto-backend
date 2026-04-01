from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import LoanableCoin, Loan
from .serializers import LoanableCoinSerializer, LoanRequestSerializer, LoanHistorySerializer


class LoanableCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Fetch loanable coins",
        responses={200: LoanableCoinSerializer(many=True)},
    )
    def get(self, request):
        coins = LoanableCoin.objects.all()
        serializer = LoanableCoinSerializer(coins, many=True)
        return Response(serializer.data)


class RequestLoanView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Request a loan",
        request_body=LoanRequestSerializer,
        responses={201: "Loan requested successfully"},
    )
    def post(self, request):
        serializer = LoanRequestSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Loan requested successfully"}, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)


class LoanHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Fetch loan history",
        responses={200: LoanHistorySerializer(many=True)},
    )
    def get(self, request):
        loans = Loan.objects.filter(user=request.user).order_by("-timestamp")
        serializer = LoanHistorySerializer(loans, many=True)
        return Response(serializer.data)
