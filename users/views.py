from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import (
                    AddressForm, 
                    CustomUserCreationForm, 
                    UserUpdateForm, 
                    ProfileUpdateForm
                    )
from .models import Profile

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

# Profile creation/editing view (NO password here)
@login_required
def profile_manage(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        address_form = AddressForm(request.POST)
        if u_form.is_valid() and p_form.is_valid() and address_form.is_valid():
            u_form.save()
            p_form.save()
            address = AddressForm.save()
            profile.addresses.add(address)
            return redirect('profile')  # Redirect to profile page after completion
    else:
        u_form= UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)
        address_form = AddressForm()

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'address_form': address_form,
        'profile': profile,
    })

