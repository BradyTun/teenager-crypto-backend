from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AdminPasswordChangeForm
from .models import User
from event_hall.models import UserLink
from django.contrib.auth.models import Group

# Unregister the default Group model
admin.site.unregister(Group)


class UserLinkInlineForm(forms.ModelForm):
    """Custom form for managing linked user."""
    linked_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Linked User",
        help_text="Select a user to link with this user, or leave blank to unlink.",
    )

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """Pre-populate the linked_user field with the current linked user."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                user_link = UserLink.objects.get(user=self.instance)
                self.fields["linked_user"].initial = user_link.linked_user
            except UserLink.DoesNotExist:
                self.fields["linked_user"].initial = None

    def save(self, commit=True):
        """Override save to handle linked user logic."""
        instance = super().save(commit=False)
        linked_user = self.cleaned_data.get("linked_user")

        # Update or delete UserLink object
        if linked_user:
            UserLink.objects.update_or_create(
                user=instance, defaults={"linked_user": linked_user}
            )
        else:
            UserLink.objects.filter(user=instance).delete()

        if commit:
            instance.save()

        return instance


class UserAdmin(BaseUserAdmin):
    model = User
    form = UserLinkInlineForm
    list_display = (
        "email",
        "username",
        "user_id",
        "linked_user_display",
        "vip_level",
        "country",
        "last_login_ip",
        "is_active",
        "is_staff",
        "photo_preview",
    )
    list_filter = ("is_active", "is_staff", "country", "vip_level")
    search_fields = ("email", "username", "user_id", "country")
    ordering = ("-date_joined",)
    readonly_fields = ("user_id", "last_login_ip", "photo_preview", "password", "reset_password_link")

    def reset_password_link(self, obj):
        """
        Adds a "Reset Password" button below the password field in the admin panel.
        """
        if obj.pk:
            reset_url = reverse("admin:auth_user_password_change", args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background: #007bff; color: white; padding: 5px 10px; '
                'border-radius: 5px; text-decoration: none;">Reset Password</a>',
                reset_url
            )
        return "Save user first to enable password reset"

    reset_password_link.short_description = "Reset Password"

    fieldsets = (
        (None, {
            "fields": ("email", "password", "reset_password_link"),
        }),
        (None, {"fields": ("mode", "closed_withdrawal", "closed_trading")}),
        ("Personal Info", {
            "fields": ("username", "phone", "date_of_birth", "country", "photo", "photo_preview"),
        }),
        ("Account Details", {
            "fields": ("user_id", "linked_user", "trading_balance", "spot_balance", "normal_balance", "vip_level", "last_login_ip"),
        }),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Ensure Django correctly renders the "Reset Password" button in admin.
        """
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # If editing an existing user, ensure the password field is properly displayed.
            fieldsets = (
                (None, {"fields": ("email", "password", "reset_password_link")}),
            ) + fieldsets[1:]
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Use Django's built-in password change form when resetting password.
        """
        if obj and request.resolver_match.url_name == "auth_user_password_change":
            return AdminPasswordChangeForm(obj, **kwargs)  # Pass the correct user instance
        return super().get_form(request, obj, **kwargs)


    def linked_user_display(self, obj):
        """Display linked user information in the list view."""
        try:
            user_link = UserLink.objects.get(user=obj)
            linked_user = user_link.linked_user
            return format_html(
                '<a href="{}">{}</a>',
                reverse("admin:app_auth_user_change", args=[linked_user.id]),
                linked_user.email,
            )
        except UserLink.DoesNotExist:
            return "No Linked User"

    linked_user_display.short_description = "Linked User"

    def photo_preview(self, obj):
        """Display a small thumbnail of the user's profile photo."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;">',
                obj.photo.url
            )
        return "No Image"

    photo_preview.short_description = "Profile Photo"


# Register the updated admin class
admin.site.register(User, UserAdmin)
