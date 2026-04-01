from django.urls import path
from .views import *

urlpatterns = [
    path("coins/", AvailableCoinsView.as_view(), name="available-coins"),
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("withdraw/", WithdrawalView.as_view(), name="withdraw"),
    path("transfer/", InternalTransferView.as_view(), name="internal-transfer"),
    path("history/", TransactionHistoryView.as_view(), name="transactions-history"),
    path("noti/", UnnotifiedTransactionsView.as_view(), name="transactions-noti"),
]
