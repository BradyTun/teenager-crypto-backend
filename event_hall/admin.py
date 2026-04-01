from django.contrib import admin
from .models import VIPLevel


@admin.register(VIPLevel)
class VIPLevelAdmin(admin.ModelAdmin):
    list_display = ("level", "recharge_amount", "claim_amount")
    list_filter = ("level",)
    search_fields = ("level",)
    ordering = ("level",)
    fields = ("level", "recharge_amount", "claim_amount")
    list_editable = ("recharge_amount", "claim_amount")
    list_display_links = ("level",)

    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",),  # Optional: Add custom CSS if needed
        }


from .models import LoveRows

@admin.register(LoveRows)
class LoveRowsAdmin(admin.ModelAdmin):
    list_display = ("amount_of_love", "level_of_love", "loves_reward")
    search_fields = ("amount_of_love", "level_of_love", "loves_reward")
