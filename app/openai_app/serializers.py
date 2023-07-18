"""
Serializers for the OpenAI app
"""
from rest_framework import serializers


class ModelDataSerializer(serializers.Serializer):
    """Serializer for data in ModelListSerializer"""
    id = serializers.CharField()
    object = serializers.CharField()
    owned_by = serializers.CharField()
    permission = serializers.ListField()


class ModelListSerializer(serializers.Serializer):
    """Serializer for ModelListAPIView"""
    object = serializers.CharField(max_length=255)
    data = ModelDataSerializer(many=True)


class ModelSerializer(serializers.Serializer):
    """Serializer for ModelAPIView"""
    id = serializers.CharField(max_length=255)
    object = serializers.CharField(max_length=255)
    owned_by = serializers.CharField(max_length=255)
    permission = serializers.ListField()


class MessageSerializer(serializers.Serializer):
    """Serializer for messages in ChatCompletionRequestSerializer\
    and ChatCompletionResponseSerializer"""
    role = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    name = serializers.CharField(required=False)


class ChatCompletionRequestSerializer(serializers.Serializer):
    """Serializer for ChatCompletionAPIView requests"""
    model = serializers.CharField(required=True)
    messages = MessageSerializer(many=True, required=True)


class ChoiceSerializer(serializers.Serializer):
    """Serializer for choices in ChatCompletionResponseSerializer"""
    index = serializers.IntegerField()
    message = MessageSerializer()
    finish_reason = serializers.CharField()


class UsageSerializer(serializers.Serializer):
    """Serializer for usage in ChatCompletionResponseSerializer"""
    prompt_tokens = serializers.IntegerField()
    completion_tokens = serializers.IntegerField()
    total_tokens = serializers.IntegerField()


class ChatCompletionResponseSerializer(serializers.Serializer):
    """Serializer for ChatCompletionAPIView responses"""
    id = serializers.CharField()
    object = serializers.CharField()
    created = serializers.IntegerField()
    model = serializers.CharField()
    choices = ChoiceSerializer(many=True)
    usage = UsageSerializer()
