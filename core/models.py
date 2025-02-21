from django.db import models


class MainAccount(models.Model):
    user = models.OneToOneField("user.CustomUser", on_delete=models.CASCADE)  # Link to the user
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Balance in GEL

    def __str__(self):
        return f"{self.user.ssn}'s Main Account - {self.balance} GEL"

    def add_balance(self, amount):
        """Add GEL to the user's account"""
        if amount > 0:
            self.balance += amount
            self.save()
        else:
            raise ValueError("Amount must be positive")


class GiftCard(models.Model):
    GIFT_TYPE_CHOICES = [
        ('myself', 'For Myself'),  # Changed from 'self' to 'myself'
        ('single', 'Gift to Someone Else'),
    ]

    user = models.ForeignKey("user.CustomUser",
                             on_delete=models.CASCADE, related_name="sent_gift_cards", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gift_type = models.CharField(max_length=10, choices=GIFT_TYPE_CHOICES, default='myself')  # Changed default
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)  # Required only if 'single'
    created_at = models.DateTimeField(auto_now_add=True)
    card_code = models.CharField(max_length=255)  # This will store the card code from the API
    cvv = models.CharField(max_length=4, default='0000')  # CVV, stored as a string (it can be 3 or 4 digits)
    exp_month = models.CharField(max_length=2, default='01')  # Expiration month (2 digits)
    exp_year = models.CharField(max_length=4, default='2025')  # Expiration year (4 digits)

    def __str__(self):
        return f"GiftCard({self.user}, {self.amount}, {self.gift_type})"

