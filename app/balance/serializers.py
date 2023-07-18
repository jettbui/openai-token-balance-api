"""
Serializers for the Balance app
"""
from rest_framework import serializers
from core.models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    """Serializer for the Balance model"""
    class Meta:
        model = Balance
        fields = ('user', 'balance')
        read_only_fields = tuple('user')
