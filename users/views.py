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
    profile, created = Profile.objects.get_or_create(user=user)
    restaurant_details, _ = RestaurantDetails.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        address_form = AddressForm(request.POST)
        # get or create restaurant details instance for the profile
        r_form = RestaurantDetailsForm(request.POST, instance=restaurant_details)

        if u_form.is_valid() and p_form.is_valid() and address_form.is_valid() and r_form.is_valid():
            u_form.save()
            p_form.save()
            address = address_form.save()
            profile.addresses.add(address)
            r_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)
        address_form = AddressForm()
        r_form = RestaurantDetailsForm(instance=restaurant_details)

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'address_form': address_form,
        'profile': profile,
        'r_form': r_form,
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