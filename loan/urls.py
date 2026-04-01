from django.urls import path
from .views import LoanableCoinsView, RequestLoanView, LoanHistoryView

urlpatterns = [
    path("coins/", LoanableCoinsView.as_view(), name="loanable-coins"),
    path("request/", RequestLoanView.as_view(), name="request-loan"),
    path("history/", LoanHistoryView.as_view(), name="loan-history"),
]
