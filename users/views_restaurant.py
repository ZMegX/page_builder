from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.conf import settings
from .restaurant_forms import (
    RestaurantProfileForm,
    HeroForm,
    AboutForm,
    SocialLinkFormSet,
    OpeningHourFormSet,
    ReviewForm,
    ReviewReplyForm,
)
from locations.models import UserAddress
from django.db.models import Q
from users.models import RestaurantProfile, Order, Profile

@login_required
def restaurant_profile(request):
    Profile.objects.get_or_create(user=request.user)
    rp, _ = RestaurantProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form_id = request.POST.get("form_id")
        rp_saved = social_saved = hours_saved = logo_saved = about_saved = hero_saved = False

        if form_id == "details-form":
            rp_form = RestaurantProfileForm(request.POST, request.FILES, instance=rp)
            hero_form = HeroForm(instance=rp)
            about_form = AboutForm(instance=rp)
            if rp_form.is_valid():
                rp_form.save()
                messages.success(request, "Profile details saved.")
                rp_saved = True
            elif rp_form.errors:
                messages.error(request, "Please correct errors in profile details.")
            social_fs = SocialLinkFormSet(instance=rp, prefix="social")
            hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")
        elif form_id == "hero-form":
            hero_form = HeroForm(request.POST, request.FILES, instance=rp)
            rp_form = RestaurantProfileForm(instance=rp)
            about_form = AboutForm(instance=rp)
            if hero_form.is_valid():
                hero_form.save()
                messages.success(request, "Hero section saved.")
                hero_saved = True
            elif hero_form.errors:
                messages.error(request, "Please correct errors in hero section.")
            social_fs = SocialLinkFormSet(instance=rp, prefix="social")
            hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")
        elif form_id == "about-form":
            about_form = AboutForm(request.POST, request.FILES, instance=rp)
            rp_form = RestaurantProfileForm(instance=rp)
            hero_form = HeroForm(instance=rp)
            if about_form.is_valid():
                about_form.save()
                messages.success(request, "About section saved.")
                about_saved = True
            elif about_form.errors:
                messages.error(request, "Please correct errors in about section.")
            social_fs = SocialLinkFormSet(instance=rp, prefix="social")
            hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")
        elif form_id == "social-form":
            social_fs = SocialLinkFormSet(request.POST, instance=rp, prefix="social")
            rp_form = RestaurantProfileForm(instance=rp)
            hero_form = HeroForm(instance=rp)
            about_form = AboutForm(instance=rp)
            if social_fs.is_valid():
                social_fs.save()
                messages.success(request, "Social links saved.")
                social_saved = True
            elif social_fs.non_form_errors() or any(f.errors for f in social_fs):
                messages.error(request, "Please correct errors in social links.")
            hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")
        elif form_id == "hours-form":
            hours_fs = OpeningHourFormSet(request.POST, instance=rp, prefix="hours")
            rp_form = RestaurantProfileForm(instance=rp)
            hero_form = HeroForm(instance=rp)
            about_form = AboutForm(instance=rp)
            social_fs = SocialLinkFormSet(instance=rp, prefix="social")
            if hours_fs.is_valid():
                hours_fs.save()
                messages.success(request, "Opening hours saved.")
                hours_saved = True
            elif hours_fs.non_form_errors() or any(f.errors for f in hours_fs):
                error_msgs = []
                error_msgs += [str(e) for e in hours_fs.non_form_errors()]
                for f in hours_fs:
                    for field, errors in f.errors.items():
                        for error in errors:
                            error_msgs.append(f"{field}: {error}")
                messages.error(request, "Opening hours errors: " + "; ".join(error_msgs))
        elif form_id == "logo-form":
            rp_form = RestaurantProfileForm(request.POST, request.FILES, instance=rp)
            hero_form = HeroForm(instance=rp)
            about_form = AboutForm(instance=rp)
            if rp_form.is_valid():
                rp_form.save()
                messages.success(request, "Logo saved.")
                logo_saved = True
            elif rp_form.errors:
                messages.error(request, "Please correct errors in logo upload.")
            social_fs = SocialLinkFormSet(instance=rp, prefix="social")
            hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")
        else:
            # fallback: process all forms as before (should not happen)
            rp_form = RestaurantProfileForm(request.POST, request.FILES, instance=rp)
            hero_form = HeroForm(request.POST, request.FILES, instance=rp)
            about_form = AboutForm(request.POST, request.FILES, instance=rp)
            social_fs = SocialLinkFormSet(request.POST, instance=rp, prefix="social")
            hours_fs = OpeningHourFormSet(request.POST, instance=rp, prefix="hours")
            if rp_form.is_valid():
                rp_form.save()
                rp_saved = True
            if hero_form.is_valid():
                hero_form.save()
                hero_saved = True
            if about_form.is_valid():
                about_form.save()
                about_saved = True
            if social_fs.is_valid():
                social_fs.save()
                social_saved = True
            if hours_fs.is_valid():
                hours_fs.save()
                hours_saved = True
        # if any form was saved, reload the page to show updated data and clear POST
        if rp_saved or social_saved or hours_saved or logo_saved or about_saved or hero_saved:
            return redirect("restaurant_profile")
    else:
        # on a GET request, create unbound instances of the forms.
        rp_form = RestaurantProfileForm(instance=rp)
        hero_form = HeroForm(instance=rp)
        about_form = AboutForm(instance=rp)
        social_fs = SocialLinkFormSet(instance=rp, prefix="social")
        hours_fs = OpeningHourFormSet(instance=rp, prefix="hours")

    # fetch the saved addresses for display in the template.
    saved_addresses = UserAddress.objects.filter(restaurant_profile=rp)

    context = {
        "rp_form": rp_form,
        "hero_form": hero_form,
        "about_form": about_form,
        "social_fs": social_fs,
        "hours_fs": hours_fs,
        "saved_addresses": saved_addresses,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, "users/restaurant_profile.html", context)

def browse_restaurants(request):
    q = request.GET.get('q', '')
    restaurants = RestaurantProfile.objects.prefetch_related('addresses')
    if q:
        restaurants = restaurants.filter(
            Q(name__icontains=q) |
            Q(cuisine_type__icontains=q) |
            Q(registration_number__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(slug__icontains=q) |
            Q(addresses__formatted_address__icontains=q)
        ).distinct()
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    return render(request, 'browse_restaurants.html', {
        'restaurants': restaurants,
        'GOOGLE_MAPS_API_KEY': key,
    })

def restaurant_reviews(request, restaurant_pk):
    restaurant = get_object_or_404(RestaurantProfile, pk=restaurant_pk)
    reviews = restaurant.reviews.filter(is_approved=True)
    return render(request, "users/restaurant_reviews.html", {
        "restaurant": restaurant,
        "reviews": reviews,
    })


def leave_review(request, restaurant_pk):
    restaurant = get_object_or_404(RestaurantProfile, pk=restaurant_pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "There was an error with your review. Please check the form.")
    return redirect('home')

@login_required
def restaurant_orders_list(request):
    if not hasattr(request.user, 'restaurant_profile') or not request.user.restaurant_profile:
        return render(request, 'users/restaurant_orders_list.html', {'orders': []})

    rp = request.user.restaurant_profile

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        if order_id and status:
            order = Order.objects.filter(id=order_id, restaurant=rp).first()
            if order and status in dict(order.STATUS_CHOICES):
                order.status = status
                order.save()
                messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
            else:
                messages.error(request, "Invalid order or status.")
        return redirect("restaurant_orders_list")

    orders = Order.objects.filter(restaurant=rp).order_by('-created_at')
    return render(request, 'users/restaurant_orders_list.html', {'orders': orders})

@login_required
def restaurant_order_detail(request, order_id):
    rp = getattr(request.user, 'restaurant_profile', None)
    order = get_object_or_404(Order, id=order_id, restaurant=rp)

    if request.method == "POST":
        status = request.POST.get("status")
        if status and status in dict(order.STATUS_CHOICES):
            order.status = status
            order.save()
            messages.success(request, f"Order status updated to {order.get_status_display()}.")
        else:
            messages.error(request, "Invalid status.")
        return redirect("restaurant_order_detail", order_id=order.id)

    return render(request, 'users/restaurant_order_detail.html', {'order': order})


@login_required
def reply_to_review(request, review_id):
    """
    View for restaurant owners to reply to a review.
    Only the owner of the restaurant can reply.
    """
    from django.utils import timezone
    from users.models import Review
    
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user owns this restaurant
    if not hasattr(request.user, 'restaurant_profile') or request.user.restaurant_profile != review.restaurant:
        messages.error(request, "You don't have permission to reply to this review.")
        return redirect('restaurant_profile')
    
    if request.method == "POST":
        form = ReviewReplyForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.reply_created_at = timezone.now()
            review.save()
            messages.success(request, "Your reply has been posted successfully!")
            return redirect('manage_reviews')
        else:
            messages.error(request, "There was an error with your reply. Please try again.")
    
    return redirect('manage_reviews')


@login_required
def manage_reviews(request):
    """
    View for restaurant owners to see and manage all reviews for their restaurant
    """
    if not hasattr(request.user, 'restaurant_profile'):
        messages.error(request, "You don't have a restaurant profile.")
        return redirect('restaurant_profile')
    
    restaurant = request.user.restaurant_profile
    reviews = restaurant.reviews.all().order_by('-created_at')
    
    return render(request, 'users/manage_reviews.html', {
        'restaurant': restaurant,
        'reviews': reviews,
    })