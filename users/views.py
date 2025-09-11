from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from .forms import (
                    AddressForm, 
                    CustomUserCreationForm, 
                    UserUpdateForm, 
                    ProfileUpdateForm,
                    RestaurantDetailsForm,
                    )
from .models import Profile, RestaurantProfile, Address

def test_map(request):
    return render(request, "registration/map-test.html")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_manage(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=user)  # use user, not profile
    address_instance = profile.addresses.first()

    # Default forms: all initialized with their instances for GET or after non-matching POST
    u_form = UserUpdateForm(instance=user)
    p_form = ProfileUpdateForm(instance=profile)
    address_form = AddressForm(instance=address_instance)
    r_form = RestaurantDetailsForm(instance=restaurant_profile)

    if request.method == 'POST':
        # Save User/Profile info
        if 'save_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, "Profile info updated!")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in your profile info.")
        
        elif 'save_restaurant' in request.POST:
            r_form = RestaurantDetailsForm(request.POST, instance=restaurant_profile)
            if r_form.is_valid():
                r_form.save()
                messages.success(request, "Restaurant details updated!")
            else:
                messages.error(request, "Please correct the errors in the restaurant details form.")
            # Save Address
        elif 'save_address' in request.POST:
            address_form = AddressForm(request.POST, instance=address_instance)
            if address_form.is_valid():
                address_obj = address_form.save()
                if not profile.addresses.filter(pk=address_obj.pk).exists():
                    profile.addresses.add(address_obj)
                # Optionally ensure FK to RestaurantProfile is set to the user's restaurant_profile
                if address_obj.profile_id != restaurant_profile.id:
                    address_obj.profile = restaurant_profile
                    address_obj.save(update_fields=['profile'])
                messages.success(request, "Address updated!")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in your address.")

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'address_form': address_form,
        'r_form': r_form,
        'profile': profile,
        'restaurant_details': restaurant_profile,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    })

@login_required
def address_edit(request, address_id):
    address = get_object_or_404(
        Address, id=address_id, profile__profile__user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('profile')
    else:
        # Pre-fill address_search nicely for UX (optional)
        initial = {}
        if address.street or address.city or address.country:
            parts = [p for p in [address.street, address.city, address.state, address.zipcode, address.country] if p]
            initial['address_search'] = ", ".join(parts)
        form = AddressForm(instance=address, initial=initial)
    return render(
        request,
        'users/address_edit.html',
        {'form': form, 'address': address, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}
    )

@login_required
def address_delete(request, address_id):
    address = get_object_or_404(Address, id=address_id, profile__profile__user=request.user)
    if request.method == 'POST':
        # Remove the address from the profile, but not from other profiles
        profile = request.user.profile
        profile.addresses.remove(address)
        # Optionally, if address not linked to any profile, delete it
        if address.profiles.count() == 0:
            address.delete()
        messages.success(request, "Address removed.")
        return redirect('profile')
    return render(request, 'users/address_confirm_delete.html', {'address': address})

@login_required
def address_add_ajax(request):
    if request.method == "POST":
        address_form = AddressForm(request.POST)  # <-- FIXED
        if address_form.is_valid():
            address = address_form.save()
            address = address_form.save(commit=False)
            restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=request.user)
            address.profile = restaurant_profile
            address.save()
            try:
                user_profile = request.user.profile
                user_profile.addresses.add(address)
            except Profile.DoesNotExist:
                    pass
            address_list_html = render_to_string(
                    "users/partials/address_list.html",
                    {"addresses": request.user.profile.addresses.all()},
                    request=request
                )
            return JsonResponse({"address_list_html": address_list_html})
        else:
            errors = address_form.errors.as_ul()
            return JsonResponse({"errors": errors}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)