from collections import defaultdict
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.db.models import Avg  # Add this import
from .models import Menu, MenuItem
from users.models import RestaurantProfile, Profile
from .forms import MenuForm, MenuItemFormSet, MenuItemForm
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def get_restaurant_profile_card(request):
    restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=request.user)
    
    card_html = render_to_string(
        'partials/restaurant_card.html',
        {'restaurant_profile': restaurant_profile},
        request=request
    )
    
    return JsonResponse({'card_html': card_html})

@login_required
def create_menu(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=user)
    
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES)  # Added request.FILES for photo upload
        formset = MenuItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():  # Ensure data consistency
                    menu = form.save(commit=False)
                    menu.owner = request.user
                    menu.save()
                    
                    formset.instance = menu
                    formset.save()
                    
                messages.success(request, f'Menu "{menu.name}" created successfully!')
                return redirect("menus:menu_detail", menu_id=menu.id)
            except Exception as e:
                messages.error(request, 'An error occurred while saving the menu. Please try again.')
        else:
            # Add specific error messages
            if form.errors:
                messages.error(request, 'Please correct the menu information errors.')
            if formset.errors:
                messages.error(request, 'Please correct the menu items errors.')
    else:
        form = MenuForm()
        formset = MenuItemFormSet()
    
    return render(request, "menus/create_menu.html", {
        "form": form, 
        "formset": formset,
        "title": "Create New Menu",
        "restaurant_profile": restaurant_profile,
        "profile": profile
    })

@login_required
def menu_detail(request, pk, int):
    menu = get_object_or_404(
        Menu.objects.prefetch_related("items"),
        Q(pk=pk) & (Q(owner=request.user) | Q(is_active=True)),
        )
    
    items_by_section = defaultdict
    for item in menu.items.all():
        section = item.get_section_display().append(item)  # Gets the human-readable version

    
    context = {
        'menu': menu,
        'items_by_section': dict(items_by_section),
        'is_owner': menu.owner == request.user,
        'total_items': menu.items.count()
    }
    return render(request, "menus/menu_detail.html", context)

def public_menu_detail(request, slug: str, pk: int):
    # public endpoint: slug = owner's username
    owner = get_object_or_404(User, username=slug)
    menu = get_object_or_404(
        Menu.objects.prefetch_related("items"),
        pk=pk,
        owner=owner,
        is_active=True,
    )

    items_by_section = defaultdict(list)
    for item in menu.items.all():
        items_by_section[item.get_section_display()].append(item)

    context = {
        "menu": menu,
        "owner": owner,
        "items_by_section": dict(items_by_section),
        "is_owner": request.user.is_authenticated and menu.owner == request.user,
        "total_items": menu.items.count(),
    }
    return render(request, "restaurant_site/menu_detail.html", context)

@login_required
def edit_menu(request, pk):
    menu = get_object_or_404(Menu, id=pk, owner=request.user)  # Ensure ownership
    
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu)
        formset = MenuItemFormSet(request.POST, instance=menu)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()
                    
                messages.success(request, f'Menu "{menu.name}" updated successfully!')
                return redirect("menus:menu_detail", menu_id=menu.id)
            except Exception as e:
                messages.error(request, 'An error occurred while updating the menu.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MenuForm(instance=menu)
        formset = MenuItemFormSet(instance=menu)
    
    return render(request, "menus/edit_menu.html", {
        "form": form,
        "formset": formset,
        "menu": menu,
        "title": f"Edit {menu.name}"
    })

@login_required
def menu_list(request):
    """List all menus for the current user"""
    # Fixed: Use consistent variable name
    menus = Menu.objects.filter(owner=request.user).order_by('-created_at')
    
    # Calculate statistics
    active_menus_count = menus.filter(is_active=True).count()
    total_items_count = sum(menu.items.count() for menu in menus)
    
    # Calculate average price across all menu items for this user
    all_items = MenuItem.objects.filter(menu__in=menus)
    average_price = all_items.aggregate(avg_price=Avg('price'))['avg_price'] or 0
    
    context = {
        'menus': menus,  # Now this matches the variable name
        'active_menus_count': active_menus_count,
        'total_items_count': total_items_count,
        'average_price': average_price,
    }
    return render(request, "menus/menu_list.html", context)

@login_required
def delete_menu(request, pk):
    menu = get_object_or_404(Menu, id=pk, owner=request.user)
    
    if request.method == "POST":
        menu_name = menu.name
        menu.delete()
        messages.success(request, f'Menu "{menu_name}" deleted successfully!')
        return redirect("menus:menu_list")
    
    return render(request, "menus/delete_menu.html", {"menu": menu})

@login_required
def toggle_menu_status(request, pk):
    """Toggle active/inactive status via AJAX"""
    menu = get_object_or_404(Menu, id=pk, owner=request.user)
    
    if request.method == "POST":
        menu.is_active = not menu.is_active
        menu.save()
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_active': menu.is_active,
                'message': f'Menu {"activated" if menu.is_active else "deactivated"} successfully!'
            })
        
        # Handle regular form submissions
        status = "activated" if menu.is_active else "deactivated"
        messages.success(request, f'Menu "{menu.name}" {status} successfully!')
        return redirect("menus:menu_detail", pk=menu.id)
    
    # GET request - show confirmation page
    return render(request, "menus/toggle_menu_status.html", {"menu": menu})

def menu_item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    
    # Check if menu is active or user is owner
    if not item.menu.is_active and item.menu.owner != request.user:
        raise PermissionDenied("This menu item is not available.")
    
    context = {
        'item': item,
        'menu': item.menu,
        'is_owner': item.menu.owner == request.user
    }
    return render(request, "menus/menu_item_detail.html", context)

# Additional helper views for the menu_list template functionality

@login_required
def menu_duplicate(request, pk):
    """Duplicate an existing menu"""
    original_menu = get_object_or_404(Menu, id=pk, owner=request.user)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Create a copy of the menu
                new_menu = Menu.objects.create(
                    name=f"{original_menu.name} (Copy)",
                    description=original_menu.description,
                    owner=request.user,
                    is_active=False  # Start as inactive
                )
                
                # Copy all menu items
                for item in original_menu.items.all():
                    MenuItem.objects.create(
                        menu=new_menu,
                        name=item.name,
                        description=item.description,
                        price=item.price,
                        section=item.section,
                        is_available=item.is_available
                    )
                
                messages.success(request, f'Menu duplicated as "{new_menu.name}"!')
                return redirect("menus:edit_menu", pk=new_menu.id)
        except Exception as e:
            messages.error(request, 'An error occurred while duplicating the menu.')
            return redirect("menus:menu_list")
    
    return render(request, "menus/menu_duplicate_confirm.html", {"menu": original_menu})

@login_required
def menu_export(request, pk):
    """Export menu data (placeholder for future implementation)"""
    menu = get_object_or_404(Menu, id=pk, owner=request.user)
    
    # For now, just redirect back with a message
    messages.info(request, f'Export functionality for "{menu.name}" coming soon!')
    return redirect("menus:menu_detail", pk=menu.id)

@login_required
def add_menu_item(request, pk):  # Using pk to match your URL pattern
    """Add a new item to a menu"""
    menu = get_object_or_404(Menu, pk=pk, owner=request.user)
    
    if request.method == "POST":
        form = MenuItemForm(request.POST)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.menu = menu
            menu_item.save()
            messages.success(request, f'Menu item "{menu_item.name}" added successfully!')
            return redirect("menus:menu_detail", pk=menu.pk)
    else:
        form = MenuItemForm()
    
    return render(request, "menus/add_menu_item.html", {
        "form": form,
        "menu": menu,
        "title": f"Add Item to {menu.name}"
    })

@login_required
def my_menu(request):
    items = (
        MenuItem.objects
        .filter(menu__owner=request.user, menu__is_active=True, is_available=True)            # <- key change here
        .select_related("menu")
        .order_by("menu__name", "section", "name")
    )
    return render(request, "menus/my_menu.html", {"items": items})


