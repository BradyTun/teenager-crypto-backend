from django.contrib import admin
from .models import LoanableCoin, Loan


@admin.register(LoanableCoin)
class LoanableCoinAdmin(admin.ModelAdmin):
    list_display = ("name", "network", "pic_preview")
    search_fields = ("name", "network")
    list_filter = ("network",)

    def pic_preview(self, obj):
        if obj.pic:
            return f'<img src="{obj.pic.url}" width="50" height="50" style="border-radius: 5px;" />'
        return "No Image"
    pic_preview.allow_tags = True
    pic_preview.short_description = "Coin Image Preview"


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_email",
        "coin_name",
        "amount",
        "loan_terms",
        "total_interest",
        "repayment_amount",
        "account_type",
        "status",
        "timestamp",
    )
    search_fields = ("user__email", "coin__name", "status")
    list_filter = ("status", "account_type", "coin__network")
    readonly_fields = ("user", "timestamp", "nrc_front_preview", "nrc_back_preview")
    actions = ["mark_as_approved", "mark_as_rejected"]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

    def coin_name(self, obj):
        return obj.coin.name
    coin_name.short_description = "Coin Name"

    def nrc_front_preview(self, obj):
        if obj.nrc_front_pic:
            return f'<img src="{obj.nrc_front_pic.url}" width="200" height="200" style="border-radius: 5px;" />'
        return "No Image"
    nrc_front_preview.allow_tags = True
    nrc_front_preview.short_description = "NRC Front Preview"

    def nrc_back_preview(self, obj):
        if obj.nrc_back_pic:
            return f'<img src="{obj.nrc_back_pic.url}" width="200" height="200" style="border-radius: 5px;" />'
        return "No Image"
    nrc_back_preview.allow_tags = True
    nrc_back_preview.short_description = "NRC Back Preview"

    @admin.action(description="Mark selected loans as Approved")
    def mark_as_approved(self, request, queryset):
        queryset.update(status="Approved")

    @admin.action(description="Mark selected loans as Rejected")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status="Rejected")
