from django.contrib import admin
from .models import MainAccount, GiftCard


# Register MainAccount model
@admin.register(MainAccount)
class MainAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # Display the user and balance in the list view
    search_fields = ('user__ssn',)  # Allow search by user’s username or SSN
    list_filter = ('balance',)  # Filter by balance (you can adjust this depending on your needs)

    def save_model(self, request, obj, form, change):
        """Custom save model method to log changes or add custom behavior."""
        super().save_model(request, obj, form, change)


# Register GiftCard model
@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'card_code', 'created_at')  # Display the relevant fields
    search_fields = ('card_code',)  # Allow search by username or card code
    list_filter = ('created_at',)  # Filter by creation date

    def save_model(self, request, obj, form, change):
        """Custom save model method to log changes or add custom behavior."""
        super().save_model(request, obj, form, change)
