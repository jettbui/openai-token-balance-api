"""
Views for the Balance API.
"""
from balance.serializers import BalanceSerializer
from core.models import (
    User
)
from django.shortcuts import get_object_or_404
from rest_framework import (
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class DeductBalanceMixin:
    """Mixin that deducts the cost of the API call from the User's Balance."""

    def check_balance(self, cost: int):
        """Check if the User has sufficient Balance for a given cost."""
        user = self.request.user

        if user.balance.balance < cost:
            return False

        return True

    def deduct_balance(self, cost: int):
        """Deduct the cost of the API call from the User's Balance."""
        user = self.request.user

        if user.balance.balance < cost:
            return Response({
                'message': 'Insufficient balance.',
            }, status=status.HTTP_402_PAYMENT_REQUIRED
            )

        user.balance.balance -= cost
        user.balance.save()


class BalanceView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Views for viewing the current User's Balance."""
    serializer_class = BalanceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Retrieve the current User's Balance."""
        user = request.user
        balance = user.balance
        serializer = self.get_serializer(balance)
        return Response(serializer.data)


class IsSuperUser(permissions.BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class ManageBalanceView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Views for managing a specific User's Balance. (Superuser only)"""
    serializer_class = BalanceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsSuperUser]
    queryset = User.objects.all()

    def get_object(self):
        """Retrieve the Balance for the specified User."""
        user_id = self.kwargs['pk']
        user = get_object_or_404(User, id=user_id)
        return user.balance

    def retrieve(self, request, *args, **kwargs):
        """Retrieve and return the Balance for the specified User."""
        balance = self.get_object()
        serializer = self.get_serializer(balance)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update the Balance for the specified User."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Update the Balance for the specified User."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
