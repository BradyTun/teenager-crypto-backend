from django.urls import path
from .views import *

urlpatterns = [
    path("vip-levels/", VIPLevelListView.as_view(), name="vip-levels"),
    path("vip-levels/claim/", ClaimRewardView.as_view(), name="vip-levels-claim"),
    path('user/link/', UserLinkView.as_view(), name='user-link'),
    path('love/', LoveRowsListView.as_view(), name='love-rows'),
]
