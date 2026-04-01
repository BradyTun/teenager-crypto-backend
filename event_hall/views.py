from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import VIPLevel, UserVIP, UserLink, LoveRows
from .serializers import VIPLevelSerializer, LoveSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth import get_user_model

User = get_user_model()


class LoveRowsListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        love_rows = LoveRows.objects.all()
        serializer = LoveSerializer(love_rows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VIPLevelListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Fetch all available VIP levels. If authenticated, includes `has_claimed` and `claimable` for the user.",
        responses={200: openapi.Response(
            "List of VIP levels with claim status and claimable status if authenticated.", VIPLevelSerializer(many=True))},
    )
    def get(self, request):
        vip_levels = VIPLevel.objects.all()
        serializer = VIPLevelSerializer(vip_levels, many=True)

        if request.user.is_authenticated:
            user_total_balance = (
                request.user.spot_balance + request.user.normal_balance + request.user.trading_balance
            )

            enriched_data = []
            for level in serializer.data:
                vip_level = VIPLevel.objects.get(level=level["level"])

                # Ensure a single UserVIP entry per user and VIP level
                user_vip, created = UserVIP.objects.get_or_create(
                    user=request.user, vip_level=vip_level
                )

                enriched_data.append({
                    **level,
                    "has_claimed": user_vip.has_claimed,
                    "claimable": (
                        not user_vip.has_claimed
                        and user_total_balance >= vip_level.recharge_amount
                    ),
                })

            return Response(enriched_data)

        return Response(serializer.data)


class ClaimRewardView(APIView):
    """
    Allow the authenticated user to claim their VIP reward based on a VIP level ID.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        vip_level_id = request.data.get("vip_level_id")
        if not vip_level_id:
            return Response({"error": "VIP level ID is required."}, status=400)

        vip_level = get_object_or_404(VIPLevel, id=vip_level_id)
        user_vip = get_object_or_404(
            UserVIP, user=request.user, vip_level=vip_level.level)

        # Check if the VIP level matches the user's current VIP level
        if user.vip_level != vip_level.level-1:
            return Response({"error": "You are not eligible to claim for this VIP level."}, status=400)

        # Check if the user is eligible to claim the reward
        if user_vip.can_claim():
            if user_vip.claim_reward():
                user.vip_level = vip_level.level
                user.trading_balance += vip_level.claim_amount
                user.save()
                return Response({"message": f"Reward claimed successfully for VIP level {vip_level.level}!"})
            return Response({"error": "Failed to claim reward."}, status=400)

        return Response({"error": "Not eligible to claim reward."}, status=400)


class UserLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the authenticated user's current link."""
        try:
            user_link = UserLink.objects.get(user=request.user)
            return Response({
                "user_id": request.user.id,
                "user_username": request.user.username,
                "linked_user_id": user_link.linked_user.id,
                "linked_user_username": user_link.linked_user.username,
            }, status=200)
        except UserLink.DoesNotExist:
            # Check if someone has linked this user
            try:
                linked_to_user = UserLink.objects.get(linked_user=request.user)
                return Response({
                    "user_id": request.user.id,
                    "user_username": request.user.username,
                    "linked_user_id": linked_to_user.user.id,
                    "linked_user_username": linked_to_user.user.username,
                }, status=200)
            except UserLink.DoesNotExist:
                return Response({"error": "No link exists for this user."}, status=404)

    def post(self, request):
        """Link the authenticated user to another user."""
        linked_user_id = request.data.get("linked_user_id")
        if not linked_user_id:
            return Response({"error": "linked_user_id is required"}, status=400)

        try:
            linked_user = get_object_or_404(User, user_id=linked_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if request.user.id == linked_user.id:
            return Response({"error": "You cannot link to yourself"}, status=400)

        # Check if the requesting user or the target user is already linked
        if UserLink.objects.filter(user=request.user).exists() or UserLink.objects.filter(linked_user=request.user).exists():
            return Response({"error": "You are already linked to another user."}, status=400)

        if UserLink.objects.filter(user=linked_user).exists() or UserLink.objects.filter(linked_user=linked_user).exists():
            return Response({"error": "The selected user is already linked to someone else."}, status=400)

        try:
            user_link = UserLink(user=request.user, linked_user=linked_user)
            user_link.save()
            return Response({"message": "Users linked successfully."}, status=201)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

    def delete(self, request):
        """Unlink the authenticated user."""
        try:
            user_link = UserLink.objects.get(user=request.user)
            user_link.delete()
            return Response({"message": "Link removed successfully."}, status=200)
        except UserLink.DoesNotExist:
            return Response({"error": "No link exists for this user."}, status=404)