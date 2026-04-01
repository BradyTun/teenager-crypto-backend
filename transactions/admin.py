from django.contrib import admin
from django.utils.html import format_html
from .models import Coin, Deposit, Withdrawal, InternalTransfer, TransactionHistory


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ("name", "network", "address", "qr_code_preview")
    search_fields = ("name", "network", "address")
    list_filter = ("network",)

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.qr_code.url,
            )
        return "No QR Code"
    qr_code_preview.short_description = "QR Code Preview"


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = (
        "user_email",
        "coin_name",
        "amount",
        "account_type",
        "status",
        "timestamp",
        "payment_screenshot_preview",
    )
    search_fields = ("user__email", "coin__name", "status")
    list_filter = ("status", "account_type", "coin__network")
    actions = ["mark_as_confirmed", "mark_as_rejected"]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

    def coin_name(self, obj):
        return obj.coin.name
    coin_name.short_description = "Coin Name"

    def payment_screenshot_preview(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<img src="{}" width="200" style="border-radius: 5px;" />',
                obj.payment_screenshot.url,
            )
        return "No Screenshot"
    payment_screenshot_preview.short_description = "Payment Screenshot"

    @admin.action(description="Mark selected deposits as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        for deposit in queryset:
            if deposit.status != "Confirmed":
                deposit.status = "Confirmed"
                deposit.save()

    @admin.action(description="Mark selected deposits as Rejected")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status="Rejected")


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = (
        "user_email",
        "coin_name",
        "amount",
        "account_type",
        "address",
        "status",
        "timestamp",
    )
    search_fields = ("user__email", "coin__name", "status", "address")
    list_filter = ("status", "account_type", "coin__network")
    actions = ["mark_as_confirmed", "mark_as_rejected"]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

    def coin_name(self, obj):
        return obj.coin.name
    coin_name.short_description = "Coin Name"

    @admin.action(description="Mark selected withdrawals as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        for obj in queryset:
            obj.status = "Confirmed"
            obj.save()  # This will call the custom save method

    @admin.action(description="Mark selected withdrawals as Rejected")
    def mark_as_rejected(self, request, queryset):
        for obj in queryset:
            obj.status = "Rejected"
            obj.save()  # This will call the custom save method


@admin.register(InternalTransfer)
class InternalTransferAdmin(admin.ModelAdmin):
    list_display = ("user_email", "account_from", "account_to", "amount", "timestamp")
    search_fields = ("user__email", "account_from", "account_to")
    list_filter = ("account_from", "account_to")

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_type",
        "user_email",
        "amount",
        "currency",
        "status",
        "network",
        "tx_id",
        "account_from",
        "account_to",
        "timestamp",
    )
    search_fields = (
        "user__email",
        "transaction_type",
        "currency",
        "network",
        "tx_id",
        "status",
    )
    list_filter = ("transaction_type", "status", "network")

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"
