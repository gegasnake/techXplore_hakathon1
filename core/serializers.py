from decimal import Decimal

from rest_framework import serializers
from .models import MainAccount, GiftCard


class MainAccountSerializer(serializers.ModelSerializer):
    # Including the user's ssn and phone number
    ssn = serializers.CharField(source='user.ssn', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = MainAccount
        fields = ['balance', 'ssn', 'phone_number']


class AddBalanceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label="Amount to Add (GEL)")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class GiftCardSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.00"))

    class Meta:
        model = GiftCard
        fields = ['amount', 'gift_type', 'recipient_phone', 'created_at']

    def validate(self, data):
        gift_type = data.get('gift_type')
        recipient_phone = data.get('recipient_phone')

        # If the gift_type is 'single', recipient_phone is required
        if gift_type == 'single' and not recipient_phone:
            raise serializers.ValidationError({"recipient_phone": "This field is required for single gifts."})

        # If the gift_type is 'myself', skip phone validation
        if gift_type != 'myself' and recipient_phone and not self.is_valid_phone_number(recipient_phone):
            raise serializers.ValidationError({"recipient_phone": "Invalid phone number format."})

        return data

    def is_valid_phone_number(self, phone):
        # Implement phone number validation logic if needed
        return True


class GiftCardSerializer_fetch(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = ['cvv', 'exp_month', 'exp_year', 'card_code']

