from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Listing(models.Model):
    LISTING_TYPE_CHOICES = (
        ('hotel', 'Hotel'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('resort', 'Resort'),
        ('cabin', 'Cabin'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    max_guests = models.IntegerField()
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('listing-detail', kwargs={'pk': self.pk})
        
class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    listings = models.ManyToManyField(Listing, related_name='amenities')
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = 'Amenities' 