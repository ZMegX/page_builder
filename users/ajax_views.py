from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import Address, Profile, RestaurantProfile
from .forms import AddressForm


@login_required
def address_get_ajax(request, address_id):
    """
    Return JSON for an address owned by the current user, to prefill the modal for editing.
    """
    address = get_object_or_404(
        Address,
        id=address_id,
        profile__profile__user=request.user  # ownership check via RestaurantProfile -> Profile -> User
    )
    data = {
        "id": address.id,
        "street": address.street or "",
        "city": address.city or "",
        "state": address.state or "",
        "zipcode": address.zipcode or "",
        "country": address.country or "",
        "latitude": float(address.latitude) if address.latitude is not None else "",
        "longitude": float(address.longitude) if address.longitude is not None else "",
        "formatted": str(address),
    }
    return JsonResponse(data)


@login_required
def address_update_ajax(request, address_id):
    """
    Update an existing address via AJAX, then return the refreshed list partial.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    address = get_object_or_404(
        Address,
        id=address_id,
        profile__profile__user=request.user
    )

    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
        address_obj = form.save(commit=False)
        # Ensure FK to the current user's RestaurantProfile
        restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=request.user)
        address_obj.profile = restaurant_profile
        address_obj.save()

        # Ensure it's linked in the user's Profile M2M
        try:
            user_profile = request.user.profile
            if not user_profile.addresses.filter(pk=address_obj.pk).exists():
                user_profile.addresses.add(address_obj)
        except Profile.DoesNotExist:
            pass

        # Refresh list HTML
        addresses = request.user.profile.addresses.all()
        address_list_html = render_to_string(
            "users/partials/address_list.html",
            {"addresses": addresses},
            request=request
        )
        return JsonResponse({"address_list_html": address_list_html})

    return JsonResponse({"errors": form.errors.as_ul()}, status=400)