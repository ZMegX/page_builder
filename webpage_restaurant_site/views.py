from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from users.models import Order
from menus.models import MenuItem
from users.models import RestaurantProfile
from django.http import HttpResponseRedirect, Http404
import calendar
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from users.models import RestaurantProfile, User
from menus.models import Menu, MenuItem
from locations.models import UserAddress
from django.db.models import Q


def is_customer(user):
    return user.is_authenticated and user.groups.filter(name='Customer').exists()

@login_required
@user_passes_test(is_customer)
def place_order(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    restaurant = item.menu.restaurant
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        special_instructions = request.POST.get('special_instructions', '')
        total_price = item.price * quantity
        order = Order.objects.create(
            customer=request.user,
            restaurant=restaurant,
            total_price=total_price,
            special_instructions=special_instructions,
        )
        order.items.add(item)
        order.save()
        messages.success(request, f"Order placed for {quantity} x {item.name}!")
        return redirect(reverse('webpage_restaurant_site:menu', kwargs={'slug': restaurant.slug}))
    return render(request, 'webpage_restaurant_site/place_order.html', {'item': item, 'request': request})
    
# def restaurant_landing(request, slug):
#     profile = get_object_or_404(
#         RestaurantProfile.objects.select_related("user").prefetch_related("addresses", "social_links", "opening_hours"),
#         slug=slug
#     )

def redirect_to_restaurant_slug(request, username):
    try:
        user = User.objects.get(username=username)
        profile = user.restaurant_profile
        if profile and profile.slug:
            return HttpResponseRedirect(f"/r/{profile.slug}/")
        else:
            raise Http404("No restaurant profile or slug found for this user.")
    except (User.DoesNotExist, RestaurantProfile.DoesNotExist):
        raise Http404("User or restaurant profile not found.")
    
def _primary_address(profile: RestaurantProfile):
    """
    Gets the most recently created address for the profile.
    """
    return profile.addresses.order_by('-created_at').first()

def _opening_status(profile: RestaurantProfile):
    """
    Computes today's hours and whether the restaurant is open now.
    """
    today_name = calendar.day_name[timezone.localdate().weekday()]
    today_hours = [oh for oh in profile.opening_hours.all() if oh.day_of_week == today_name]
    now_local = timezone.localtime().time()
    open_now = any(
        (oh.open_time <= now_local <= oh.close_time) if oh.open_time and oh.close_time and oh.open_time < oh.close_time
        else (now_local >= oh.open_time or now_local <= oh.close_time) if oh.open_time and oh.close_time
        else False
        for oh in today_hours
    )
    return {"today_name": today_name, "today_hours": today_hours, "open_now": open_now}

def _slug_fallback(profile: RestaurantProfile) -> str:
    return profile.slug if profile and profile.slug else None

def restaurant_landing(request, slug):
    """
    renders the public landing page for a restaurant, including map and details.
    passes all hero, about and popular menu item context for dynamics sections.
    """
    print("\n--- DEBUG: restaurant_landing view entered ---")
    print(f"1. SLUG: '{slug}'")
    
    profile = RestaurantProfile.objects.select_related("user").get(slug=slug)    
    print(f"2. RESTAURANTPROFILE FOUND: {profile.name if profile else 'None'}")

    if profile:
        all_addresses = list(profile.addresses.all())
        print(f"3. ALL ADDRESSES FOR PROFILE ({len(all_addresses)}): {all_addresses}")
    else:
        all_addresses = []
        print("3. ALL ADDRESSES FOR PROFILE: Profile is None, so no addresses.")

    address = _primary_address(profile) if profile else None
    print(f"4. PRIMARY ADDRESS CHOSEN: {address if address else 'None'}")
    
    status = _opening_status(profile) if profile else {}

    lat = float(address.latitude) if address and hasattr(address, 'latitude') and address.latitude is not None else None
    lng = float(address.longitude) if address and hasattr(address, 'longitude') and address.longitude is not None else None
    print(f"5. COORDINATES: lat={lat}, lng={lng}")

    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    print(f"6. GOOGLE MAPS API KEY IS SET: {bool(key)}")
    print("--- DEBUG: END ---\n")

    popular_items = (
        MenuItem.objects.filter(menu__owner=profile.user, popular_items=True)
        .order_by('-menu__is_active', '-menu__name', 'price')[:2]
    )
    if not popular_items:
        popular_items = (
            MenuItem.objects.filter(menu__owner=profile.user)
            .order_by('-menu__is_active', '-menu__name', 'price')[:2]
        )

    context = {
        "profile": profile,
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": key,
        "map_center": {"lat": lat, "lng": lng},
        "slug": _slug_fallback(profile) if profile else "",
        # for hero section
        "hero_headline": getattr(profile, "hero_headline", None),
        "hero_description": getattr(profile, "hero_description", None),
        "hero_image": getattr(profile, "hero_image", None),
        # For about section
        "about_headline": getattr(profile, "about_headline", None),
        "about_description": getattr(profile, "about_description", None),
        "about_image": getattr(profile, "about_image", None),
        "about_highlight": getattr(profile, "about_highlight", None),
        # For menu section
        "popular_items": popular_items,
    }
    return render(request, "webpage_restaurant_site/landing.html", context)

def restaurant_menu(request, slug):
    """
    Renders the public menu page for a restaurant.
    """
    profile = get_object_or_404(RestaurantProfile.objects.select_related("user"), slug=slug)
    menus = (Menu.objects
             .filter(owner=profile.user, is_active=True)
             .prefetch_related("items")
             .order_by("name"))

    address = _primary_address(profile)
    status = _opening_status(profile)
    lat = float(address.latitude) if address and hasattr(address, 'latitude') and address.latitude is not None else None
    lng = float(address.longitude) if address and hasattr(address, 'longitude') and address.longitude is not None else None
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")

    is_customer = request.user.is_authenticated and request.user.groups.filter(name='Customer').exists()
    context = {
        "profile": profile,
        "menus": menus,
        "slug": _slug_fallback(profile) if profile else "",
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": key,
        "map_center": {"lat": lat, "lng": lng},
        "is_customer": is_customer,
    }
    return render(request, "webpage_restaurant_site/menu.html", context)

def restaurant_contact(request, slug):
    """
    Renders the public contact page for a restaurant.
    """
    profile = get_object_or_404(RestaurantProfile.objects.select_related("user"), slug=slug)
    address = _primary_address(profile)
    status = _opening_status(profile)
    lat = float(address.latitude) if address and hasattr(address, 'latitude') and address.latitude is not None else None
    lng = float(address.longitude) if address and hasattr(address, 'longitude') and address.longitude is not None else None
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")

    context = {
        "profile": profile,
        "slug": _slug_fallback(profile) if profile else "",
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": key,
        "map_center": {"lat": lat, "lng": lng},
    }
    return render(request, "webpage_restaurant_site/contact.html", context)

def restaurant_about(request, slug):
    """
    Renders the public about page for a restaurant.
    """
    profile = get_object_or_404(RestaurantProfile.objects.select_related("user"), slug=slug)
    address = _primary_address(profile)
    status = _opening_status(profile)
    lat = float(address.latitude) if address and hasattr(address, 'latitude') and address.latitude is not None else None
    lng = float(address.longitude) if address and hasattr(address, 'longitude') and address.longitude is not None else None
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")

    context = {
        "profile": profile,
        "slug": _slug_fallback(profile) if profile else "",
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": key,
        "map_center": {"lat": lat, "lng": lng},
    }
    return render(request, "webpage_restaurant_site/about.html", context)

def order_online(request, slug):
    """
    Renders the public order online page for a restaurant.
    """
    profile = get_object_or_404(RestaurantProfile.objects.select_related("user"), slug=slug)
    address = _primary_address(profile)
    status = _opening_status(profile)
    lat = float(address.latitude) if address and hasattr(address, 'latitude') and address.latitude is not None else None
    lng = float(address.longitude) if address and hasattr(address, 'longitude') and address.longitude is not None else None
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")

    context = {
        "profile": profile,
        "slug": _slug_fallback(profile) if profile else "",
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": key,
        "map_center": {"lat": lat, "lng": lng},
    }
    return render(request, "webpage_restaurant_site/order_online.html", context)