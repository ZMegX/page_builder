from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.conf import settings
from .restaurant_forms import (
    RestaurantProfileForm,
    SocialLinkFormSet,
    OpeningHourFormSet,
    RestaurantProfileForm,
    ReviewForm,
)
from locations.models import UserAddress
from django.db.models import Q
from users.models import RestaurantProfile, Order, Profile

@login_required
def restaurant_profile(request):
    Profile.objects.get_or_create(user=request.user)
    rp, _ = RestaurantProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # All forms are bound to the same POST data.
        rp_form = RestaurantProfileForm(request.POST, request.FILES, instance=rp)
        social_fs = SocialLinkFormSet(request.POST, instance=rp, prefix="social")
        hours_fs = OpeningHourFormSet(request.POST, instance=rp, prefix="hours")

        # Validate all forms together.
        if rp_form.is_valid() and social_fs.is_valid() and hours_fs.is_valid():
            rp_form.save()
            social_fs.save()
            hours_fs.save()
            messages.success(request, "Your profile has been saved successfully.")
            return redirect("restaurant_profile")
        else:
            # If any form is invalid, show an error.
            messages.error(request, "Please correct the errors below.")
    else:
        # On a GET request, create unbound instances of the forms.
        rp_form = RestaurantProfileForm(instance=rp)
        social_fs = SocialLinkFormSet(instance=rp, prefix="social")
        hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")

    # Fetch the saved addresses for display in the template.
    saved_addresses = UserAddress.objects.filter(restaurant_profile=rp)

    context = {
        "rp_form": rp_form,
        "social_fs": social_fs,
        "hours_fs": hours_fs,
        "saved_addresses": saved_addresses,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, "users/restaurant_profile.html", context)

def browse_restaurants(request):
    q = request.GET.get('q', '')
    restaurants = RestaurantProfile.objects.prefetch_related('addresses')
    if q:
        restaurants = restaurants.filter(
            Q(name__icontains=q) |
            Q(cuisine_type__icontains=q) |
            Q(registration_number__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(slug__icontains=q) |
            Q(addresses__formatted_address__icontains=q)
        ).distinct()
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    return render(request, 'browse_restaurants.html', {
        'restaurants': restaurants,
        'GOOGLE_MAPS_API_KEY': key,
    })

def restaurant_reviews(request, restaurant_pk):
    restaurant = get_object_or_404(RestaurantProfile, pk=restaurant_pk)
    reviews = restaurant.reviews.filter(is_approved=True)
    return render(request, "users/restaurant_reviews.html", {
        "restaurant": restaurant,
        "reviews": reviews,
    })


def leave_review(request, restaurant_pk):
    restaurant = get_object_or_404(RestaurantProfile, pk=restaurant_pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "There was an error with your review. Please check the form.")
    return redirect('home')

@login_required
def restaurant_orders_list(request):
    if not hasattr(request.user, 'restaurant_profile') or not request.user.restaurant_profile:
        return render(request, 'users/restaurant_orders_list.html', {'orders': []})

    rp = request.user.restaurant_profile

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        if order_id and status:
            order = Order.objects.filter(id=order_id, restaurant=rp).first()
            if order and status in dict(order.STATUS_CHOICES):
                order.status = status
                order.save()
                messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
            else:
                messages.error(request, "Invalid order or status.")
        return redirect("restaurant_orders_list")

    orders = Order.objects.filter(restaurant=rp).order_by('-created_at')
    return render(request, 'users/restaurant_orders_list.html', {'orders': orders})

@login_required
def restaurant_order_detail(request, order_id):
    rp = getattr(request.user, 'restaurant_profile', None)
    order = get_object_or_404(Order, id=order_id, restaurant=rp)
    return render(request, 'users/restaurant_order_detail.html', {'order': order})