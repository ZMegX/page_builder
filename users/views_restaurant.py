from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from .models import RestaurantProfile, Profile
from .restaurant_forms import (
    RestaurantProfileForm,
    SocialLinkFormSet,
    OpeningHourFormSet,
    RestaurantProfileForm,
)
from locations.models import UserAddress


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