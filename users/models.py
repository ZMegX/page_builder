
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from locations.models import CustomerAddress
from django.utils.text import slugify


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey('users.RestaurantProfile', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    pay_method = models.CharField(max_length=50, blank=True, null=True)  

    def __str__(self):
        return f'Order #{self.id} by {self.customer} for {self.restaurant}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey('menus.MenuItem', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price at time of order
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for Order #{self.order.id}"

class SocialLink(models.Model):
    profile = models.ForeignKey('RestaurantProfile', on_delete=models.CASCADE, related_name='social_links')
    name = models.CharField(max_length=50)   # e.g., 'Instagram'
    url = models.URLField()

    def __str__(self):
        display = self.profile.name if getattr(self.profile, "name", None) else "Restaurant"
        return f"{self.name} ({display})"

class OpeningHour(models.Model):
    profile = models.ForeignKey('RestaurantProfile', on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.CharField(max_length=10)  # e.g., 'Monday'
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day_of_week}: {self.open_time} - {self.close_time}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('Profile picture', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

THEME_CHOICES = [
    ('synthwave', 'Synthwave'),
    ('elegant', 'Elegant'),
    ('minimal', 'Minimal'),
    ('default', 'Default'),
    # Add more themes as needed
]

class RestaurantProfile(models.Model):
    class Meta:
        verbose_name = "Restaurant Profile"
        verbose_name_plural = "Restaurant Profiles"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_profile', null=True, blank=True)
    profile = models.OneToOneField('Profile', null=True, blank=True, on_delete=models.CASCADE, related_name='restaurant_details')
    name = models.CharField(max_length=200, blank=True, null=True)
    logo = CloudinaryField('Restaurant logo', blank=True, null=True)
    cuisine_type = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    hero_headline = models.CharField(max_length=120, blank=True, null=True,
        help_text="Headline for the hero section on the landing page."
    )
    hero_description = models.TextField(blank=True, null=True,
        help_text="Short description for the hero section."
    )
    hero_image = CloudinaryField('Hero image', blank=True, null=True, 
        help_text="Background image for the hero section."
    )
    about_headline = models.CharField(max_length=120, blank=True, null=True,
        help_text="Headline for the About Us section."
    )
    about_description = models.TextField(blank=True, null=True,
        help_text="Description for the About Us section."
    )
    about_image = CloudinaryField('About image', blank=True, null=True,
        help_text="Image for the About Us section."
    )
    about_highlight = models.CharField(max_length=120, blank=True, null=True,
        help_text="Highlighted quote or fact for the About Us section."
    )
    theme_choice = models.CharField(max_length=32, choices=THEME_CHOICES, default='default',
        help_text="Select the theme for your restaurant page."
    )
    def __str__(self):
        if self.profile and self.profile.user:
            return f"{self.profile.user.username} Restaurant Details"
        return f"{self.name or 'Unnamed'} Restaurant"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.name
            if not base:
                if self.profile and self.profile.user:
                    base = self.profile.user.username
                elif self.user and self.user.username:
                    base = self.user.username
                else:
                    base = str(self.pk or '')
            self.slug = slugify(base)
        super().save(*args, **kwargs)


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    full_name = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = CloudinaryField('Profile picture', blank=True, null=True)
    default_address = models.ForeignKey(CustomerAddress, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    preferences = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Review(models.Model):
    restaurant = models.ForeignKey(RestaurantProfile, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reviewer_name = models.CharField(max_length=100, blank=True)  # For anonymous reviews
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # For moderation, if needed

    def __str__(self):
        return f"Review for {self.restaurant.name}: {self.rating} stars"

    class Meta:
        ordering = ['-created_at']