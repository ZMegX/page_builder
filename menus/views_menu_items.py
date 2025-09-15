from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Menu, MenuItem
from .forms import MenuItemForm


def build_menu_context(menu, user):
    items_by_section = group_items_by_section(menu.items.all())
    return {
        'menu': menu,
        'items_by_section': items_by_section,
        'sections_ordered': sorted(items_by_section.keys()),
        'is_owner': menu.owner == user,
        'total_items': menu.items.count()
    }

def get_menu_item_with_permission(item_id, user):
    item = get_object_or_404(MenuItem, id=item_id)
    if not item.menu.is_active and item.menu.owner != user:
        raise PermissionDenied("This menu item is not available.")
    return item

def group_items_by_section(items):
    from collections import defaultdict
    items_by_section = defaultdict(list)
    for item in items:
        section_label = item.get_section_display() if hasattr(item, "get_section_display") else getattr(item, "section", "Uncategorized")
        items_by_section[section_label].append(item)
    return dict(items_by_section)

@login_required
def add_menu_item(request, pk):
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

def menu_item_detail(request, item_id):
    item = get_menu_item_with_permission(item_id, request.user)
    context = {
        'item': item,
        'menu': item.menu,
        'is_owner': item.menu.owner == request.user
    }
    return render(request, "menus/menu_item_detail.html", context)
