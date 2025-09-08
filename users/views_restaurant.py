from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from .models import RestaurantProfile
from .restaurant_forms import (
    RestaurantProfileForm,
    AddressForm,
    SocialLinkFormSet,
    OpeningHourFormSet,
)



@login_required
def restaurant_profile(request):
    rp, _ = RestaurantProfile.objects.get_or_create(user=request.user)
    address_instance = rp.addresses.first() if rp.addresses.exists() else None

    def make_forms(bound=None):
        """
        bound can be: 'rp', 'addr', 'social', 'hours', 'all', or None
        Only the specified section is bound to POST; others are unbound to avoid showing their errors.
        """
        bind_rp = request.POST if bound in ('rp', 'all') else None
        bind_addr = request.POST if bound in ('addr', 'all') else None
        bind_social = request.POST if bound in ('social', 'all') else None
        bind_hours = request.POST if bound in ('hours', 'all') else None

        rp_form = RestaurantProfileForm(bind_rp, request.FILES if bind_rp is not None else None, instance=rp)

        # Address initial text for display when unbound
        initial = {}
        if address_instance and bound not in ('addr', 'all'):
            parts = [p for p in [address_instance.street, address_instance.city, address_instance.state,
                                 address_instance.zipcode, address_instance.country] if p]
            if parts:
                initial["address_search"] = ", ".join(parts)

        addr_form = AddressForm(bind_addr, instance=address_instance, initial=initial)
        social_fs = SocialLinkFormSet(bind_social, instance=rp, prefix="social")
        hours_fs = OpeningHourFormSet(bind_hours, instance=rp, prefix="hours")
        return rp_form, addr_form, social_fs, hours_fs

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

        elif 'save_addr' in request.POST:
            rp_form, addr_form, social_fs, hours_fs = make_forms(bound='addr')
            if addr_form.is_valid():
                addr = addr_form.save(commit=False)
                addr.profile = rp
                addr.save()
                messages.success(request, "Address saved.")
                return redirect("restaurant_profile")
            else:
                messages.error(request, "Please fix the errors in Address.")

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

        elif 'save_all' in request.POST:
            # Try to save each section independently; save what’s valid, show errors for the rest
            rp_form, addr_form, social_fs, hours_fs = make_forms(bound='all')
            saved, failed = [], []

            if rp_form.is_valid():
                rp_form.save()
                saved.append("details")
            else:
                failed.append("details")

            if addr_form.is_valid():
                addr = addr_form.save(commit=False)
                addr.profile = rp
                addr.save()
                saved.append("address")
            else:
                failed.append("address")

            if social_fs.is_valid():
                social_fs.save()
                saved.append("social")
            else:
                failed.append("social")

            if hours_fs.is_valid():
                hours_fs.save()
                saved.append("hours")
            else:
                failed.append("hours")

            if saved:
                messages.success(request, f"Saved: {', '.join(saved)}.")
            if failed:
                messages.error(request, f"Issues in: {', '.join(failed)}. Please review highlighted fields.")

            # If everything succeeded, redirect (PRG)
            if not failed:
                return redirect("restaurant_profile")

        else:
            # Fallback: treat as saving details
            rp_form, addr_form, social_fs, hours_fs = make_forms(bound='rp')
            if rp_form.is_valid():
                rp_form.save()
                messages.success(request, "Restaurant details saved.")
                return redirect("restaurant_profile")
            else:
                messages.error(request, "Please fix the errors in Restaurant Details.")

    else:
        rp_form, addr_form, social_fs, hours_fs = make_forms(bound=None)

    return render(request, "users/restaurant_profile.html", {
        "rp_form": rp_form,
        "addr_form": addr_form,
        "social_fs": social_fs,
        "hours_fs": hours_fs,
        "GOOGLE_MAPS_API_KEY": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
    })