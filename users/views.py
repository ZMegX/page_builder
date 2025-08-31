from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import (
                    AddressForm, 
                    CustomUserCreationForm, 
                    UserUpdateForm, 
                    ProfileUpdateForm,
                    RestaurantDetailsForm
                    )
from .models import Profile, RestaurantDetails, Address

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
    restaurant_details, _ = RestaurantDetails.objects.get_or_create(profile=profile)

    # Get the first address if it exists
    address_instance = profile.addresses.first()

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        address_form = AddressForm(request.POST, instance=address_instance)
        r_form = RestaurantDetailsForm(request.POST, instance=restaurant_details)

        if u_form.is_valid():
            u_form.save()
        if p_form.is_valid():
            p_form.save()
        if address_form.is_valid():
            profile.addresses.add(address_form.save())  
            r_form.save()
        messages.success(request, "Your profile has been updated!")

        return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)
        address_form = AddressForm(instance=address_instance)
        r_form = RestaurantDetailsForm(instance=restaurant_details)

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'address_form': address_form,
        'r_form': r_form,
        'profile': profile,
        'restaurant_details': restaurant_details,
    })

@login_required
def address_edit(request, address_id):
    address = get_object_or_404(Address, id=address_id, profiles__user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'users/address_edit.html', {'form': form, 'address': address})

@login_required
def address_delete(request, address_id):
    address = get_object_or_404(Address, id=address_id, profiles__user=request.user)
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
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save()
            # Add to current user's profile
            profile = request.user.profile
            profile.addresses.add(address)
            # Render updated addresses list partial
            address_list_html = render_to_string(
                "users/partials/address_list.html",
                {"profile": profile},
                request=request
            )
            return JsonResponse({"address_list_html": address_list_html})
        else:
            errors = address_form.errors.as_ul()
            return JsonResponse({"errors": errors}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)