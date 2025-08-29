from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import (
                    AddressForm, 
                    CustomUserCreationForm, 
                    UserUpdateForm, 
                    ProfileUpdateForm,
                    RestaurantDetailsForm
                    )
from .models import Profile, RestaurantDetails

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

