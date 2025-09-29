from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Order
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.conf import settings
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
from .restaurant_forms import ( ReviewForm, )
from .models import Profile, RestaurantProfile, SocialLink, OpeningHour, Review
from locations.models import UserAddress
from django.db.models import Q
from django.forms import modelformset_factory
from django.contrib.auth.models import Group
import json
from django.urls import reverse

def is_restaurant_owner(user):
    return hasattr(user, 'restaurant_profile') and user.restaurant_profile is not None

@login_required
@user_passes_test(is_restaurant_owner)
def restaurant_orders_list(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        if order_id and status:
            try:
                order = Order.objects.get(id=order_id, restaurant=request.user.restaurant_profile)
                order.status = status
                order.save()
                # Send email to customer
                from django.core.mail import send_mail
                subject = f"Your order #{order.id} status has been updated"
                message = f"Hello {order.customer.username},\n\nYour order status is now: {order.get_status_display()}.\n\nThank you for ordering from {order.restaurant.name}."
                recipient_list = [order.customer.email]
                send_mail(subject, message, None, recipient_list, fail_silently=True)
                messages.success(request, "Order status updated and customer notified.")
            except Order.DoesNotExist:
                messages.error(request, "Order not found.")
        return redirect('restaurant_orders_list')
    orders = Order.objects.filter(restaurant=request.user.restaurant_profile).order_by('-created_at')
    return render(request, 'users/restaurant_orders_list.html', {'orders': orders})

def is_restaurant_owner(user):
    return user.is_authenticated and user.groups.filter(name='RestaurantOwner').exists()

def is_customer(user):
    return user.is_authenticated and user.groups.filter(name='Customer').exists()

def documentation(request):
    return render(request, 'users/docs.html')

def why_choose_us(request):
    return render(request, 'users/why_choose_us.html')

def home(request):
    q = request.GET.get('q', '')
    restaurants_qs = RestaurantProfile.objects.prefetch_related('addresses')
    if q:
        restaurants_qs = restaurants_qs.filter(
            Q(name__icontains=q) |
            Q(cuisine_type__icontains=q) |
            Q(registration_number__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(slug__icontains=q) |
            Q(addresses__formatted_address__icontains=q)
        ).distinct()
    print("--- DEBUG: home view entered ---")
    print(f"Search query: '{q}'")
    print(f"Restaurant count: {restaurants_qs.count()}")
    for r in restaurants_qs:
        print(f"- {r.name} | Cuisine: {r.cuisine_type} | Slug: {r.slug} | Addresses: {r.addresses.count()}")
        for addr in r.addresses.all():
            print(f"  Formatted Address: {addr.formatted_address}")
    print("--- DEBUG: END ---")
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")

    # No pagination: get all restaurants
    restaurants = list(restaurants_qs)

    print('--- DEBUG: All restaurants and their addresses ---')
    for r in restaurants:
        print(f'Restaurant: {r.name}')
        for addr in r.addresses.all():
            print(f'  Address: {addr.formatted_address}, lat={addr.latitude}, lng={addr.longitude}')

    # Update restaurant_reviews to work with list
    restaurant_reviews = {r.pk: r.reviews.filter(is_approved=True) for r in restaurants}

    # Prepare addresses for map
    addresses = []
    for r in restaurants:
        for addr in r.addresses.all():
            if r.slug:
                restaurant_url = reverse('webpage_restaurant_site:landing', kwargs={'slug': r.slug})
            else:
                restaurant_url = '#'
            addresses.append({
                'name': r.name,
                'address': addr.formatted_address,
                'lat': addr.latitude if addr.latitude is not None else None,
                'lng': addr.longitude if addr.longitude is not None else None,
                'cuisine': r.cuisine_type,
                'slug': r.slug,
                'logo': r.logo.url if getattr(r.logo, 'url', None) else '',
                'url': restaurant_url
            })
    print(f"Addresses for map: {addresses}")
    addresses_json = json.dumps(addresses)
    print(f"addresses_json for JS: {addresses_json}")

    review_form = ReviewForm(request.POST or None)
    if request.method == "POST" and review_form.is_valid():
        review = review_form.save(commit=False)

        if request.user.is_authenticated:
            review.user = request.user
        review.save()
        messages.success(request, "Thank you for your review!")

    restaurant_reviews = {r.pk: r.reviews.filter(is_approved=True) for r in restaurants}
    
    return render(request, 'home.html', {
        'restaurants': restaurants,
        'GOOGLE_MAPS_API_KEY': key,
        'review_form': review_form,
        'restaurant_reviews': restaurant_reviews,
        'addresses_json': addresses_json,
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            Profile.objects.get_or_create(user=user)
            if role == 'customer':
                from users.models import CustomerProfile
                CustomerProfile.objects.create(user=user)
                group, _ = Group.objects.get_or_create(name='Customer')
            else:
                from users.models import RestaurantProfile
                RestaurantProfile.objects.create(user=user)
                group, _ = Group.objects.get_or_create(name='RestaurantOwner')
            user.groups.add(group)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_manage(request):
    """
    Manages the user's personal profile information (username, email, picture).
    Restaurant-related details are managed in the restaurant_profile view.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        u_valid = u_form.is_valid()
        p_valid = p_form.is_valid()

        if u_valid:
            u_form.save()
            messages.success(request, "Your user info has been updated successfully!")
        if p_valid:
            p_form.save()
            messages.success(request, "Your profile info has been updated successfully!")

        if u_valid or p_valid:
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
    # Fetch restaurant details for display purposes only.
    try:
        restaurant_details = RestaurantProfile.objects.get(user=request.user)
    except RestaurantProfile.DoesNotExist:
        restaurant_details = None

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'restaurant_details': restaurant_details,
    }
    return render(request, 'users/profile.html', context)

@login_required
def address_edit(request, address_id):
    address = get_object_or_404(
        UserAddress, id=address_id, profile__profile__user=request.user)
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
    address = get_object_or_404(UserAddress, id=address_id, profile__profile__user=request.user)
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

@login_required
def restaurant_profile_manage(request):
    restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=request.user)
    SocialLinkFormSet = modelformset_factory(SocialLink, fields=('name', 'url'), extra=1, can_delete=True)
    OpeningHourFormSet = modelformset_factory(OpeningHour, fields=('day_of_week', 'open_time', 'close_time'), extra=1, can_delete=True)

    if request.method == 'POST':
        rp_form = RestaurantDetailsForm(request.POST, request.FILES, instance=restaurant_profile)
        social_fs = SocialLinkFormSet(request.POST, queryset=restaurant_profile.social_links.all())
        hours_fs = OpeningHourFormSet(request.POST, queryset=restaurant_profile.opening_hours.all())

        valid = rp_form.is_valid() and social_fs.is_valid() and hours_fs.is_valid()
        if valid:
            rp_form.save()
            social_fs.save()
            hours_fs.save()
            messages.success(request, "Your restaurant profile has been updated!")
            return redirect('restaurant_profile_manage')
    else:
        rp_form = RestaurantDetailsForm(instance=restaurant_profile)
        social_fs = SocialLinkFormSet(queryset=restaurant_profile.social_links.all())
        hours_fs = OpeningHourFormSet(queryset=restaurant_profile.opening_hours.all())

    context = {
        'rp_form': rp_form,
        'social_fs': social_fs,
        'hours_fs': hours_fs,
        'saved_addresses': restaurant_profile.addresses.all(),
        'GOOGLE_MAPS_API_KEY': getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
    }
    return render(request, 'users/restaurant_profile.html', context)