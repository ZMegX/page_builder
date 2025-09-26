from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from users.models import Order, OrderItem
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
def place_order(request):
    # Multi-item checkout: process all items in the cart
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('webpage_restaurant_site:cart')

    if request.method == 'POST':
        special_instructions = request.POST.get('special_instructions', '')
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        # Assume all items are from the same restaurant
        first_item_id = next(iter(cart))
        first_item = get_object_or_404(MenuItem, id=first_item_id)
        restaurant = RestaurantProfile.objects.get(user=first_item.menu.owner)

        # store order details in session for confirmation
        request.session['order_details'] = {
            'cart': cart,
            'special_instructions': special_instructions,
            'checkout_option': None,
            'total_price': total_price,
            'restaurant_slug': restaurant.slug,
        }
        messages.success(request, "Order placed successfully! Please confirm your order.")
        return redirect('webpage_restaurant_site:order_confirmation')

    return render(request, 'webpage_restaurant_site/place_order.html', {'cart': cart, 'request': request})

    return render(request, 'webpage_restaurant_site/place_order.html', {'cart': cart, 'request': request})

@login_required
@user_passes_test(is_customer)
def order_confirmation(request):

    order_details = request.session.get('order_details', None)
    # If order_details is missing, populate it from cart and redirect to self
    if not order_details:
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect('webpage_restaurant_site:cart')
        # Calculate total and get restaurant info
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        first_item_id = next(iter(cart))
        first_item = get_object_or_404(MenuItem, id=first_item_id)
        restaurant = RestaurantProfile.objects.get(user=first_item.menu.owner)
        order_details = {
            'cart': cart,
            'special_instructions': '',
            'checkout_option': None,
            'total_price': total_price,
            'restaurant_slug': restaurant.slug,
        }
        request.session['order_details'] = order_details
        # Redirect to self to ensure context is loaded
        return redirect('webpage_restaurant_site:order_confirmation')

    cart = order_details.get('cart', {})
    total_price = order_details.get('total_price', 0)
    special_instructions = order_details.get('special_instructions', '')
    checkout_option = order_details.get('checkout_option', None)
    restaurant_slug = order_details.get('restaurant_slug', '')
    order_status = request.session.get('order_status', 'Pending')

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('webpage_restaurant_site:cart')

    if request.method == 'POST':
        # Guest chooses delivery/takeout and payment method
        pay_method = request.POST.get('pay_method')
        option = request.POST.get('option')
        if not pay_method or not option:
            messages.error(request, "Please select both delivery/takeout and payment method before confirming your order.")
        else:
            order_details['checkout_option'] = option
            request.session['order_details'] = order_details
            cart = order_details['cart']
            special_instructions = order_details.get('special_instructions', '')
            total_price = order_details.get('total_price', 0)
            first_item_id = next(iter(cart))
            first_item = get_object_or_404(MenuItem, id=first_item_id)
            restaurant = RestaurantProfile.objects.get(user=first_item.menu.owner)
            # Create the order now
            order = Order.objects.create(
                customer=request.user,
                restaurant=restaurant,
                total_price=total_price,
                special_instructions=special_instructions,
                status='Pending',
                # fulfillment_option=option, # Uncomment if your model supports this
                # payment_method=pay_method, # Uncomment if your model supports this
            )
            for item_id, item_data in cart.items():
                menu_item = get_object_or_404(MenuItem, id=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                    notes=item_data.get('notes', '')
                )
            order.save()
            request.session['cart'] = {}
            request.session['order_details'] = {}
            request.session['order_id'] = order.id
            request.session['order_status'] = 'Preparing'
            messages.success(request, "Order confirmed! Please pay by cash upon delivery or pickup.")
            return redirect('webpage_restaurant_site:checkout')

    is_customer = request.user.is_authenticated and request.user.groups.filter(name='Customer').exists()
    return render(request, 'webpage_restaurant_site/order_confirmation.html', {
        'cart': cart,
        'checkout_option': checkout_option,
        'total_price': total_price,
        'special_instructions': special_instructions,
        'restaurant_slug': restaurant_slug,
        'order_status': order_status,
        'is_customer': is_customer,
    })

@login_required
@user_passes_test(is_customer)
def checkout(request):
    order_id = request.session.get('order_id')
    order = None
    cart = {}
    total_price = 0
    checkout_option = None
    order_number = None
    order_status = request.session.get('order_status', 'Pending')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order_number = order.id
        # Reconstruct cart from order items
        for item in order.order_items.all():
            cart[str(item.menu_item.id)] = {
                'name': item.menu_item.name,
                'price': float(item.price),
                'quantity': item.quantity,
                'notes': item.notes,
            }
        total_price = order.total_price
        # Try to get checkout_option from session or order (if you store it)
        checkout_option = request.session.get('order_details', {}).get('checkout_option', None)
    else:
        messages.error(request, "No order found.")
        return redirect('webpage_restaurant_site:cart')

    if request.method == 'POST':
        # Finalize order, show thank you or payment page
        messages.success(request, "Thank you for your order!")
        # Optionally clear order session info
        request.session['order_id'] = None
        request.session['order_status'] = None
        return redirect('webpage_restaurant_site:menu', slug=order.restaurant.slug)

    is_customer = request.user.is_authenticated and request.user.groups.filter(name='Customer').exists()
    return render(request, 'webpage_restaurant_site/checkout.html', {
        'order': order,
        'cart': cart,
        'total_price': total_price,
        'checkout_option': checkout_option,
        'order_number': order_number,
        'order_status': order_status,
        'is_customer': is_customer,
    })

@login_required
@user_passes_test(is_customer)
@require_POST
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(item_id), {'name': item.name, 'price': float(item.price), 'quantity': 0})
    cart_item['quantity'] += 1
    cart[str(item_id)] = cart_item
    request.session['cart'] = cart
    messages.success(request, f"Added {item.name} to cart.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@user_passes_test(is_customer)
def cart_display(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    # Do not fetch RestaurantProfile for the current user (customer)
    return render(request, 'webpage_restaurant_site/cart.html', {'cart': cart, 'total': total})

@login_required
@user_passes_test(is_customer)
@require_POST
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    return redirect('webpage_restaurant_site:cart')

@login_required
@user_passes_test(is_customer)
@require_POST
def update_cart(request, item_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] = quantity
        request.session['cart'] = cart
        messages.success(request, "Cart updated.")
    return redirect('webpage_restaurant_site:cart')


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