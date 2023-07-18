"""
Views for the OpenAI API.
"""
import openai
import openai_app.serializers as serializers
import tiktoken
from balance.views import DeductBalanceMixin
from django.conf import settings
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from rest_framework import (
    status,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

openai.organization = settings.OPENAI_ORGANIZATION
openai.api_key = settings.OPENAI_API_KEY


class ModelListAPIView(APIView):
    """Reference: https://platform.openai.com/docs/api-reference/models/list"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ModelListSerializer

    def get(self, request):
        """Lists the currently available models, and provides basic\
        information about each one such as the owner and availability."""
        try:
            response = openai.Model.list()
            serializer = self.serializer_class(response)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelAPIView(APIView):
    """
    Reference:
    https://platform.openai.com/docs/api-reference/models/retrieve
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ModelSerializer

    def get(self, request, model=None):
        """Retrieves a model instance, providing basic information\
        about the model such as the owner and permissioning."""
        try:
            response = openai.Model.retrieve(model)
            serializer = self.serializer_class(response)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatCompletionAPIView(APIView):
    """Reference: https://platform.openai.com/docs/api-reference/chat/create"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ChatCompletionRequestSerializer

    def post(self, request, model=None, max_tokens=None):
        """Creates a model response for the given chat conversation."""
        model = request.data.get('model', None)
        messages = request.data.get('messages', None)
        user_max_tokens = request.data.get('max_tokens', None)

        if user_max_tokens and max_tokens:
            max_tokens = min(max_tokens, user_max_tokens)
        elif user_max_tokens:
            max_tokens = user_max_tokens

        # Check with serializer if the request is valid.
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )

            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def num_tokens_from_messages(messages, model='gpt-3.5-turbo-0613'):
    """
    Return the number of tokens used by a list of messages.
    Reference:
    https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Default to cl100k_base encoding
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 4
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # gpt-3.5-turbo may update over time.
        # Returning num tokens assuming gpt-3.5-turbo-0613.
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""
            num_tokens_from_messages() is not implemented for model \
            {model}. See \
            https://github.com/openai/openai-python/blob/main/chatml.md \
            for information on how messages are converted to tokens.
            """
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


class DeductibleChatCompletionAPIView(
    DeductBalanceMixin,
    ChatCompletionAPIView,
):
    """
    ChatCompletionAPIView that deducts the cost \
    of the API call from the User's Balance.
    """

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=serializers.ChatCompletionResponseSerializer
            )
        }
    )
    def post(self, request, model=None):
        """Creates a model response for the given chat conversation."""
        user = request.user
        user_balance = user.balance.balance
        model = request.data.get('model', None)
        messages = request.data.get('messages', None)

        input_cost = 0
        if messages and type(messages) == list:
            input_cost = num_tokens_from_messages(messages, model=model)

        if not self.check_balance(input_cost):
            return Response({
                'message': 'Insufficient balance.',
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # Make the API call only if the User has sufficient Balance.
        res = super().post(request, model, max_tokens=user_balance-input_cost)

        if res.status_code == status.HTTP_200_OK:
            outputCost = res.data.get('usage').get('completion_tokens') or 0
            self.deduct_balance(input_cost + outputCost)

        return res
