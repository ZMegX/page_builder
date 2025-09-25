from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class Menu(models.Model):
    name = models.CharField(max_length=100)
    photo = CloudinaryField(
        'image',
        transformation={
            'width': 800,
            'height': 600,
            'crop': 'fill',
            'quality': 'auto'
        },
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class MenuItem(models.Model):
    SECTION_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('main', 'Main Courses'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('dessert', 'Dessert'),
        ('drinks', 'Drinks'),
        ('appetizers', 'Appetizers'),
        ('sides', 'Sides'),
        ('specials', 'Specials'),
        ('vegan', 'Vegan'),
        ('gluten_free', 'Gluten Free'),
        ('kids', "Kids' Menu"),
        ('hot_drinks', 'Hot Drinks')
    ]
    
    menu = models.ForeignKey(Menu, related_name="items", on_delete=models.CASCADE)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    order = models.PositiveIntegerField(default=0, help_text="Order of this item within its section")
    name = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    ingredients = models.TextField(max_length=200, default="Fresh ingredients", help_text="List main ingredients")
    is_available = models.BooleanField(default=True, help_text="Whether this item is currently available for ordering")
    image = CloudinaryField(
        'Menu Item Image',
        null=True,
        blank=True,
        help_text="Optional image for the menu item."
    )
    popular_items = models.BooleanField(default=False, help_text="Mark this item as a popular dish")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    class Meta:
        ordering = ['section', 'order', 'name']