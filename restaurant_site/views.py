import calendar
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth import get_user_model
from users.models import RestaurantProfile
from menus.models import Menu  # uses Menu.restaurant -> RestaurantProfile

User = get_user_model()

def _get_profile(slug: str) -> RestaurantProfile:
    """
    Resolve profile by RestaurantProfile.slug, then user.username, then pk.
    Adjust if your model differs.
    """
    qs = (RestaurantProfile.objects
          .select_related("user")
          .prefetch_related("addresses", "social_links", "opening_hours"))
    try:
        return qs.get(slug=slug)
    except Exception:
        pass
    try:
        return qs.get(user__username=slug)
    except Exception:
        pass
    try:
        return qs.get(pk=int(slug))
    except Exception:
        pass
    return get_object_or_404(qs, slug=slug)

def _primary_address(profile: RestaurantProfile):
    return profile.addresses.first()

def _opening_status(profile: RestaurantProfile):
    """
    Compute today's hours and whether it's open now.
    """
    today_name = calendar.day_name[timezone.localdate().weekday()]
    today_hours = [oh for oh in profile.opening_hours.all() if oh.day_of_week == today_name]
    now_local = timezone.localtime().time()
    open_now = False
    current_interval = None
    for oh in today_hours:
        if oh.open_time and oh.close_time and oh.open_time < oh.close_time:
            if oh.open_time <= now_local <= oh.close_time:
                open_now = True
                current_interval = oh
                break
        # To support overnight hours uncomment:
        # elif oh.open_time and oh.close_time and oh.open_time > oh.close_time:
        #     if now_local >= oh.open_time or now_local <= oh.close_time:
        #         open_now = True
        #         current_interval = oh
        #         break
    return {
        "today_name": today_name,
        "today_hours": today_hours,
        "open_now": open_now,
        "current_interval": current_interval,
    }

def _slug_fallback(profile: RestaurantProfile) -> str:
    return getattr(profile, "slug", None) or getattr(profile.user, "username", None) or str(profile.pk)

def restaurant_landing(request, slug):
    profile = _get_profile(slug)
    address = _primary_address(profile)
    status = _opening_status(profile)

    lat = float(address.latitude) if address and address.latitude is not None else None
    lng = float(address.longitude) if address and address.longitude is not None else None

    context = {
        "profile": profile,
        "address": address,
        "status": status,
        "GOOGLE_MAPS_API_KEY": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
        "map_center": {"lat": lat, "lng": lng},
        "profile_slug": _slug_fallback(profile),
    }
    return render(request, "restaurant_site/landing.html", context)

def restaurant_menu(request, slug):
    owner = get_object_or_404(User, username=slug)
    menus = (Menu.objects
             .filter(owner=owner, is_active=True)
             .prefetch_related("items")
             .order_by("name"))
    profile = getattr(owner, "restaurant_profile", None)
    return render(request, 
        "restaurant_site/menu.html", 
        {
            "owner": owner,
            "menus": menus,
            "profile": profile,
            "slug": owner.username,
        },   
    )

def landing(request, slug):
    owner = get_object_or_404(User, username=slug)
    profile = getattr(owner, "restaurant_profile", None)
    return render(request, "restaurant_site/landing.html", {"owner": owner, "profile": profile, "slug": owner.username})