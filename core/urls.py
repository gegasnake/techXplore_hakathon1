from django.urls import path

from core.views import AddBalanceAPIView, MainAccountView, CreateGiftCardView, UserGiftCardsView

urlpatterns = [
    path('add_balance/', AddBalanceAPIView.as_view(), name='add_balance'),
    path('main_account/', MainAccountView.as_view(), name='main_account'),
    path('create_gift_card/', CreateGiftCardView.as_view(), name='create_gift_card'),
    path('gift-cards/', UserGiftCardsView.as_view(), name='user-gift-cards'),
]
