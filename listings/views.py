from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .models import Listing, Amenity
from django.db.models import Q

class ListingListView(ListView):
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'
    ordering = ['-created_at']
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Listing.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(listing_type__icontains=query)
            ).filter(is_available=True).order_by('-created_at')
        return Listing.objects.filter(is_available=True).order_by('-created_at')

class ListingDetailView(DetailView):
    model = Listing
    template_name = 'listings/listing_detail.html'
    
class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    template_name = 'listings/listing_form.html'
    fields = ['title', 'description', 'price', 'location', 'listing_type', 
              'bedrooms', 'bathrooms', 'max_guests', 'image']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
        
class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    template_name = 'listings/listing_form.html'
    fields = ['title', 'description', 'price', 'location', 'listing_type', 
              'bedrooms', 'bathrooms', 'max_guests', 'image', 'is_available']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
        
    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.owner
        
class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = 'listings/listing_confirm_delete.html'
    success_url = reverse_lazy('listing-list')
    
    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.owner
        
def user_listings(request, username):
    user = get_object_or_404(User, username=username)
    listings = Listing.objects.filter(owner=user).order_by('-created_at')
    return render(request, 'listings/user_listings.html', {'listings': listings, 'user': user}) 