from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.conf import settings

from .models import RestaurantProfile, Profile
from .restaurant_forms import (
    RestaurantProfileForm,
    SocialLinkFormSet,
    OpeningHourFormSet,
    RestaurantProfileForm,
    ReviewForm,
)
from locations.models import UserAddress
from django.db.models import Q
from users.models import Review



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