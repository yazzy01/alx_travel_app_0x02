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
from .models import Listing, Amenity, Booking, Payment
from django.db.models import Q
import requests
import json
import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
from datetime import datetime

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

@login_required
def create_booking(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.method == 'POST':
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        guests = request.POST.get('guests')
        
        # Calculate total price based on listing price and duration
        check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        duration = (check_out - check_in).days
        total_price = listing.price * duration
        
        # Create booking
        booking = Booking.objects.create(
            listing=listing,
            user=request.user,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guests=guests,
            total_price=total_price,
            status='pending'
        )
        
        # Initiate payment
        return redirect('initiate_payment', booking_id=booking.id)
    
    return render(request, 'listings/create_booking.html', {'listing': listing})

@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Create payment record
    payment = Payment.objects.create(
        booking=booking,
        amount=booking.total_price,
        status='pending'
    )
    
    # Initiate payment with Chapa API
    chapa_secret_key = os.environ.get('CHAPA_SECRET_KEY', 'CHAPA_SECRET_KEY_HERE')
    chapa_api_url = 'https://api.chapa.co/v1/transaction/initialize'
    
    headers = {
        'Authorization': f'Bearer {chapa_secret_key}',
        'Content-Type': 'application/json'
    }
    
    tx_ref = str(uuid.uuid4())
    payment.payment_reference = tx_ref
    payment.save()
    
    payload = {
        'amount': str(payment.amount),
        'currency': payment.currency,
        'tx_ref': tx_ref,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'callback_url': request.build_absolute_uri(reverse_lazy('verify_payment', kwargs={'payment_reference': tx_ref})),
        'return_url': request.build_absolute_uri(reverse_lazy('payment_success', kwargs={'payment_reference': tx_ref})),
        'customization': {
            'title': f'Booking for {booking.listing.title}',
            'description': f'Payment for booking from {booking.check_in_date} to {booking.check_out_date}'
        }
    }
    
    try:
        response = requests.post(chapa_api_url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status') == 'success':
            payment.transaction_id = response_data.get('data', {}).get('tx_ref')
            payment.save()
            
            # Redirect to Chapa payment page
            checkout_url = response_data.get('data', {}).get('checkout_url')
            return redirect(checkout_url)
        else:
            # Handle payment initiation failure
            payment.status = 'failed'
            payment.save()
            return render(request, 'listings/payment_failed.html', {'error': response_data.get('message', 'Payment initiation failed')})
    
    except Exception as e:
        # Handle exceptions
        payment.status = 'failed'
        payment.save()
        return render(request, 'listings/payment_failed.html', {'error': str(e)})

@csrf_exempt
def verify_payment(request, payment_reference):
    payment = get_object_or_404(Payment, payment_reference=payment_reference)
    
    # Verify payment with Chapa API
    chapa_secret_key = os.environ.get('CHAPA_SECRET_KEY', 'CHAPA_SECRET_KEY_HERE')
    chapa_verify_url = f'https://api.chapa.co/v1/transaction/verify/{payment_reference}'
    
    headers = {
        'Authorization': f'Bearer {chapa_secret_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(chapa_verify_url, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status') == 'success':
            # Update payment status
            payment.status = 'completed'
            payment.save()
            
            # Update booking status
            booking = payment.booking
            booking.status = 'confirmed'
            booking.save()
            
            # Send confirmation email
            send_payment_confirmation_email(payment)
            
            return JsonResponse({'status': 'success', 'message': 'Payment verified successfully'})
        else:
            # Handle verification failure
            payment.status = 'failed'
            payment.save()
            return JsonResponse({'status': 'error', 'message': response_data.get('message', 'Payment verification failed')})
    
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'status': 'error', 'message': str(e)})

def payment_success(request, payment_reference):
    payment = get_object_or_404(Payment, payment_reference=payment_reference)
    return render(request, 'listings/payment_success.html', {'payment': payment})

def send_payment_confirmation_email(payment):
    subject = f'Payment Confirmation for Booking #{payment.booking.booking_reference}'
    message = f'''
    Dear {payment.booking.user.first_name},
    
    Your payment for booking #{payment.booking.booking_reference} has been confirmed.
    
    Booking Details:
    - Listing: {payment.booking.listing.title}
    - Check-in Date: {payment.booking.check_in_date}
    - Check-out Date: {payment.booking.check_out_date}
    - Guests: {payment.booking.guests}
    - Total Amount: {payment.amount} {payment.currency}
    - Transaction ID: {payment.transaction_id}
    
    Thank you for using our service!
    
    Best regards,
    ALX Travel App Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [payment.booking.user.email]
    
    # Use Celery to send email in background (if configured)
    try:
        from listings.tasks import send_email_task
        send_email_task.delay(subject, message, from_email, recipient_list)
    except ImportError:
        # Fallback to sending email synchronously
        send_mail(subject, message, from_email, recipient_list, fail_silently=False) 