from django.urls import path
from .views import (
    ListingListView,
    ListingDetailView,
    ListingCreateView,
    ListingUpdateView,
    ListingDeleteView,
    user_listings
)

urlpatterns = [
    path('', ListingListView.as_view(), name='listing-list'),
    path('listing/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('listing/new/', ListingCreateView.as_view(), name='listing-create'),
    path('listing/<int:pk>/update/', ListingUpdateView.as_view(), name='listing-update'),
    path('listing/<int:pk>/delete/', ListingDeleteView.as_view(), name='listing-delete'),
    path('user/<str:username>/listings/', user_listings, name='user-listings'),
] 