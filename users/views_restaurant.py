from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from .models import RestaurantProfile, Profile
from .restaurant_forms import (
    RestaurantProfileForm,
    SocialLinkFormSet,
    OpeningHourFormSet,
)

@login_required
def restaurant_profile(request):
    Profile.objects.get_or_create(user=request.user)
    rp, _ = RestaurantProfile.objects.get_or_create(user=request.user)

    def make_forms(bound=None):
        """
        bound can be: 'rp', 'addr', 'social', 'hours', 'all', or None
        Only the specified section is bound to POST; others are unbound to avoid showing their errors.
        """
        bind_rp = request.POST if bound in ('rp', 'all') else None
        bind_social = request.POST if bound in ('social', 'all') else None
        bind_hours = request.POST if bound in ('hours', 'all') else None

        rp_form = RestaurantProfileForm(bind_rp, request.FILES if bind_rp is not None else None, instance=rp)
        social_fs = SocialLinkFormSet(bind_social, instance=rp, prefix="social")
        hours_fs = OpeningHourFormSet(bind_hours, instance=rp, prefix="hours")
        
        return rp_form, social_fs, hours_fs

    if request.method == "POST":
        # Which section was submitted?
        if 'save_rp' in request.POST:
            rp_form, addr_form, social_fs, hours_fs = make_forms(bound='rp')
            if rp_form.is_valid():
                rp_form.save()
                messages.success(request, "Restaurant details saved.")
                return redirect("restaurant_profile")
            else:
                messages.error(request, "Please fix the errors in Restaurant Details.")

        elif 'save_social' in request.POST:
            rp_form, addr_form, social_fs, hours_fs = make_forms(bound='social')
            if social_fs.is_valid():
                social_fs.save()
                messages.success(request, "Social links saved.")
                return redirect("restaurant_profile")
            else:
                messages.error(request, "Please fix the errors in Social Links.")

        elif 'save_hours' in request.POST:
            rp_form, addr_form, social_fs, hours_fs = make_forms(bound='hours')
            if hours_fs.is_valid():
                hours_fs.save()
                messages.success(request, "Opening hours saved.")
                return redirect("restaurant_profile")
            else:
                messages.error(request, "Please fix the errors in Opening Hours.")
        else:
            # Fallback if no specific button is identified
            rp_form, social_fs, hours_fs = make_forms()
            messages.warning(request, "Could not process the form. Please try again.")
    else:
        # For a GET request, just show the unbound forms.
        rp_form, social_fs, hours_fs = make_forms()

    # The list of saved addresses is now fetched for display purposes only.
        saved_addresses = rp.addresses.all()
    

    return render(request, "users/restaurant_profile.html", {
        "rp_form": rp_form,
        "saved_addresses": saved_addresses,
        "social_fs": social_fs,
        "hours_fs": hours_fs,
        "GOOGLE_MAPS_API_KEY": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
    })