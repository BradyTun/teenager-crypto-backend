from django import forms
from django.contrib import admin
from .models import Duration, Trade

class DurationInputWidget(forms.TextInput):
    """
    A custom widget for DurationField that expects input in HH:MM:SS format.
    """
    def format_value(self, value):
        if isinstance(value, str):
            return value  # Already in string format
        if value is None:
            return ""
        # Convert timedelta to HH:MM:SS
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

class DurationForm(forms.ModelForm):
    duration = forms.DurationField(
        widget=DurationInputWidget(attrs={"placeholder": "HH:MM:SS"})
    )

    class Meta:
        model = Duration
        fields = "__all__"

@admin.register(Duration)
class DurationAdmin(admin.ModelAdmin):
    form = DurationForm
    list_display = ("duration", "win_percentage")
    search_fields = ("duration",)
    list_filter = ("win_percentage",)

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("user", "trade_method", "amount", "selected_duration", "profit_or_loss", "is_closed", "opened_at")
    search_fields = ("user__email", "trade_method", "amount", "selected_duration")
    list_filter = ("is_closed", "trade_method",)
    readonly_fields = ("profit_or_loss", "opened_at", "selected_duration")

    def selected_duration(self, obj):
        """
        Converts the related Duration object's timedelta to a human-readable string.
        """
        td = obj.duration.duration
        total_seconds = int(td.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} min{'s' if minutes > 1 else ''}")

        return " ".join(parts) or "0 min"

    selected_duration.short_description = "Selected Duration"
