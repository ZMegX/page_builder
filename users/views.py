from django.shortcuts import render, redirect
from .forms import (ProfileForm, 
                    AddressForm, 
                    UserCreationForm,
                    UserRegisterForm, 
                    CustomUserCreationForm,
                    UserUpdateForm,
                    ProfileUpdateForm,
                    )
from .models import Profile
from django.contrib.auth.decorators import login_required

@login_required
def create_profile(request):
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(user=request.user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        except Profile.DoesNotExist:
            profile_form = ProfileForm(request.POST, request.FILES)
        
        address_form = AddressForm(request.POST)
        
        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            address = address_form.save()
            profile.addresses.add(address)
            return redirect('registration/complete_profile')
    else:
        try:
            profile = Profile.objects.get(user=request.user)
            profile_form = ProfileForm(instance=profile)
        except Profile.DoesNotExist:
            profile_form = ProfileForm()
        address_form = AddressForm()
    return render(request, 'registration/registration.html', {
        'profile_form': profile_form,
        'address_form': address_form
    })

@login_required
def complete_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        address_form = AddressForm(request.POST)
        if profile_form.is_valid() and address_form.is_valid():
            profile_form.save()
            address = address_form.save()
            profile.addresses.add(address)
            return redirect('dashboard')
    else:
        profile_form = ProfileForm(instance=profile)
        address_form = AddressForm()
    return render(request, 'registration/complete_profile.html', {
        'profile_form': profile_form,
        'address_form': address_form
    })

@login_required
def profile(request):
  if request.method == 'POST':
    u_form = UserUpdateForm(request.POST, instance=request.user)
    p_form = ProfileUpdateForm(request.POST, 
                request.FILES, 
                instance=request.user.profile)
    if u_form.is_valid() and p_form.is_valid():
      u_form.save()
      p_form.save()
      messages.success(request, f'Your account has been updated') #Changes here
      return redirect('profile') #Changes here
  else:
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)

  context = {
    'u_form': u_form,
    'p_form': p_form
  }

  return render(request, 'users/profile.html', context)


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')