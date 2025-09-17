from django.http import HttpResponseRedirect, Http404
import calendar
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from users.models import RestaurantProfile, User
from menus.models import Menu
from locations.models import UserAddress
from django.db.models import Q

    
def restaurant_landing(request, slug):
    profile = get_object_or_404(
        RestaurantProfile.objects.select_related("user").prefetch_related("addresses", "social_links", "opening_hours"),
        slug=slug
    )

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
    Renders the public landing page for a restaurant, including map and details.
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

    context = {
        "profile": profile,
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": key,
        "map_center": {"lat": lat, "lng": lng},
        "slug": _slug_fallback(profile) if profile else "",
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

    return render(request, 
        "webpage_restaurant_site/menu.html", 
        {
            "profile": profile,
            "menus": menus,
            "slug": _slug_fallback(profile) if profile else "",
        },   
    )

