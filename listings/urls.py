from django.urls import path
from .views import (
    ListingListView,
    ListingDetailView,
    ListingCreateView,
    ListingUpdateView,
    ListingDeleteView,
    user_listings,
    create_booking,
    initiate_payment,
    verify_payment,
    payment_success
)

urlpatterns = [
    path('', ListingListView.as_view(), name='listing-list'),
    path('listing/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('listing/new/', ListingCreateView.as_view(), name='listing-create'),
    path('listing/<int:pk>/update/', ListingUpdateView.as_view(), name='listing-update'),
    path('listing/<int:pk>/delete/', ListingDeleteView.as_view(), name='listing-delete'),
    path('user/<str:username>/listings/', user_listings, name='user-listings'),
    path('listing/<int:listing_id>/book/', create_booking, name='create-booking'),
    path('booking/<int:booking_id>/payment/', initiate_payment, name='initiate_payment'),
    path('payment/verify/<str:payment_reference>/', verify_payment, name='verify_payment'),
    path('payment/success/<str:payment_reference>/', payment_success, name='payment_success'),
] 