import logging

from .serializers import AddBalanceSerializer, MainAccountSerializer, GiftCardSerializer_fetch

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from .models import MainAccount, GiftCard
from .serializers import GiftCardSerializer
from decimal import Decimal, InvalidOperation
from user.models import CustomUser
logger = logging.getLogger(__name__)
from techXplore_hakathon1.settings import CLOUDFLARE_SECRET_KEY

class CreateGiftCardView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GiftCardSerializer

    def post(self, request):
        # CAPTCHA verification

        captcha_response = request.POST.get("cf-turnstile-response")
        data = {"secret": CLOUDFLARE_SECRET_KEY, "response": captcha_response}
        captcha_verification = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
        captcha_result = captcha_verification.json()

        if not captcha_result.get("success"):
            return Response({"detail": "Invalid CAPTCHA."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract data from request
        amount = request.data.get('amount')
        gift_type = request.data.get('gift_type', 'myself')  # Default to 'self'
        recipient_phone = request.data.get('recipient_phone')

        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except (ValueError, InvalidOperation):
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= Decimal('0.00'):
            return Response({"detail": "Amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        if gift_type == 'single':
            if not recipient_phone:
                return Response({"detail": "Recipient phone number is required for single gifts."},
                                status=status.HTTP_400_BAD_REQUEST)
            recipient = CustomUser.objects.filter(phone_number=recipient_phone).first()
            if not recipient:
                return Response({"detail": "Recipient user not found."}, status=status.HTTP_404_NOT_FOUND)
            recipient_account, _ = MainAccount.objects.get_or_create(user=recipient)

        try:
            sender_account = MainAccount.objects.get(user=request.user)
        except MainAccount.DoesNotExist:
            return Response({"detail": "Main account not found."}, status=status.HTTP_404_NOT_FOUND)

        if sender_account.balance < amount:
            return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            sender_account.balance -= amount
            sender_account.save()

            url = "https://sandbox.lithic.com/v1/cards"
            payload = {"type": "VIRTUAL"}
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "09a67168-19fe-4c0a-b273-71aa5b1f8c94"
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                card_data = response.json()
                card_code = card_data.get('token')
                cvv = card_data.get('cvv')
                exp_month = card_data.get('exp_month')
                exp_year = card_data.get('exp_year')

                if card_code and cvv and exp_month and exp_year:
                    owner = recipient if gift_type == 'single' else request.user
                    gift_card = GiftCard.objects.create(
                        user=owner,
                        amount=amount,
                        card_code=card_code,
                        cvv=cvv,
                        exp_month=exp_month,
                        exp_year=exp_year,
                        gift_type=gift_type,
                        recipient_phone=recipient_phone if gift_type == 'single' else None
                    )
                    serializer = GiftCardSerializer(gift_card)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"detail": "Failed to generate card data."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddBalanceAPIView(APIView):
    serializer_class = AddBalanceSerializer

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)

        captcha_response = request.POST.get("cf-turnstile-response")
        data = {"secret": CLOUDFLARE_SECRET_KEY, "response": captcha_response}
        captcha_verification = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
        captcha_result = captcha_verification.json()

        if not captcha_result.get("success"):
            return Response({"detail": "Invalid CAPTCHA."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddBalanceSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data["amount"]
            try:
                account, created = MainAccount.objects.get_or_create(user=request.user)
                account.add_balance(amount)
                return Response({"message": f"Successfully added {amount} GEL to your account."},
                                status=status.HTTP_200_OK)
            except MainAccount.DoesNotExist:
                return Response({"detail": "Could not find your account."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MainAccountView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MainAccountSerializer

    def get(self, request):
        try:
            # Retrieve the MainAccount for the authenticated user
            account = MainAccount.objects.get(user=request.user)
        except MainAccount.DoesNotExist:
            return Response({"detail": "Main account not found."}, status=404)

        # Serialize the account data
        serializer = MainAccountSerializer(account)
        return Response(serializer.data, status=200)


class UserGiftCardsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GiftCardSerializer_fetch

    def get(self, request):
        # Filter gift cards by the authenticated user
        user_gift_cards = GiftCard.objects.filter(user=request.user)

        # Serialize the gift cards
        serializer = GiftCardSerializer(user_gift_cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)