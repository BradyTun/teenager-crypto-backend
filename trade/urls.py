from django.urls import path
from .views import OpenTradeView, CloseTradeView, TradeHistoryView, DurationListView

urlpatterns = [
    path("open/", OpenTradeView.as_view(), name="open-trade"),
    path("close/<int:trade_id>/", CloseTradeView.as_view(), name="close-trade"),
    path("history/", TradeHistoryView.as_view(), name="trade-history"),
    path("durations/", DurationListView.as_view(), name="trade-durations"),
]
