from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Min, Max, Avg
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import Menu, MenuItem
from users.models import RestaurantProfile, Profile
from .forms import MenuForm, MenuItemFormSet, MenuItemForm
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from .models import Menu, MenuItem
from .serializers import MenuSerializer, MenuItemSerializer

def redirect_to_frontend_add_item(request):
    # Redirect to the frontend route for adding a menu item
    return redirect('/menu-editor?addItem=1')

@csrf_exempt
@require_POST
def menu_items_reorder_api(request):
    """
    Accepts a POST with JSON: [{"id": 123, "order": 0}, ...]
    Updates MenuItem.order for each item.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        for item in data:
            menu_item = MenuItem.objects.get(id=item['id'])
            menu_item.order = item['order']
            menu_item.save(update_fields=['order'])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
User = get_user_model()
# --- Helper Functions ---

def get_user_menu(pk, user):
    """Fetch a menu by pk and owner."""
    return get_object_or_404(Menu, pk=pk, owner=user)

@login_required
def get_restaurant_profile_card(request):
    restaurant_profile, _ = RestaurantProfile.objects.get_or_create(user=request.user)
    
    card_html = render_to_string(
        'partials/restaurant_card.html',
        {'restaurant_profile': restaurant_profile},
        request=request
    )
    
    return JsonResponse({'card_html': card_html})

    
class MenuDetailView(LoginRequiredMixin, DetailView):
    model = Menu
    template_name = "menus/menu_detail.html"
    context_object_name = "menu"

    def get_queryset(self):
        # Only allow owner or active menus
        user = self.request.user
        return Menu.objects.prefetch_related("items").filter(
            Q(owner=user) | Q(is_active=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu = self.object
        items_by_section = group_items_by_section(menu.items.all())
        context['items_by_section'] = items_by_section
        context['sections_ordered'] = sorted(items_by_section.keys())
        context['is_owner'] = menu.owner == self.request.user
        context['total_items'] = menu.items.count()
        return context

# Helper function needed for MenuDetailView and public_menu_detail
def group_items_by_section(items):
    from collections import defaultdict
    items_by_section = defaultdict(list)
    for item in items:
        section_label = item.get_section_display() if hasattr(item, "get_section_display") else getattr(item, "section", "Uncategorized")
        items_by_section[section_label].append(item)
    return dict(items_by_section)

def public_menu_detail(request, slug: str):
    # public endpoint: slug = restaurant's slug
    restaurant_profile = get_object_or_404(RestaurantProfile, slug=slug)
    menus = Menu.objects.prefetch_related("items").filter(
        owner=restaurant_profile.user,
        is_active=True,
    )

    context = {
        "menus": menus,
        "restaurant_profile": restaurant_profile,
        "is_owner": request.user.is_authenticated and restaurant_profile.user == request.user,
    }
    return render(request, "restaurant_site/menus_list.html", context)

# class MenuUpdateView(LoginRequiredMixin, UpdateView):
#     model = Menu
#     form_class = MenuForm
#     template_name = "menus/edit_menu.html"
#     context_object_name = "menu"

#     def get_queryset(self):
#         # Only allow the owner to edit
#         return Menu.objects.filter(owner=self.request.user)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         menu = self.object
#         if self.request.method == "POST":
#             context["formset"] = MenuItemFormSet(self.request.POST, instance=menu)
#         else:
#             context["formset"] = MenuItemFormSet(instance=menu)
#         context["title"] = f"Edit {menu.name}"
#         return context

#     def form_valid(self, form):
#         menu = form.save()
#         formset = MenuItemFormSet(self.request.POST, instance=menu)
#         if formset.is_valid():
#             formset.save()
#             messages.success(self.request, f'Menu "{menu.name}" updated successfully!')
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)
    
#     def get_success_url(self):
#         return reverse_lazy("menus:menu_detail", kwargs={"pk": self.object.pk})

class MenuListView(LoginRequiredMixin, ListView):
    model = Menu
    template_name = "menus/menu_list.html"
    context_object_name = "menus"

    def get_queryset(self):
        user = self.request.user
        sort_option = self.request.GET.get('sort', '-updated_at')
        sort_map = {
            'updated_at_desc': '-updated_at',
            'updated_at_asc': 'updated_at',
            'name_asc': 'name',
            'name_desc': '-name',
        }
        order_by_field = sort_map.get(sort_option, '-updated_at')
        return Menu.objects.filter(owner=user).annotate(
            item_count=Count('items'),
            min_price=Min('items__price'),
            max_price=Max('items__price')
        ).order_by(order_by_field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['active_menus_count'] = self.get_queryset().filter(is_active=True).count()
        context['total_items_count'] = MenuItem.objects.filter(menu__owner=user).count()
        avg_price_result = MenuItem.objects.filter(menu__owner=user).aggregate(avg_price=Avg('price'))
        context['average_price'] = avg_price_result['avg_price'] or 0
        context['is_paginated'] = False
        # Add restaurant profile to context
        if hasattr(user, 'restaurant_profile'):
            context['restaurant'] = user.restaurant_profile
        return context
    
class MenuDeleteView(LoginRequiredMixin, DeleteView):
    model = Menu
    template_name = "menus/delete_menu.html"
    context_object_name = "menu"
    success_url = reverse_lazy("menus:menu_list")

    def get_queryset(self):
        # Only allow the owner to delete
        return Menu.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        menu = self.get_object()
        messages.success(request, f'Menu "{menu.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

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
def my_menu(request):
    items = (
        MenuItem.objects
        .filter(menu__owner=request.user, menu__is_active=True, is_available=True)            # <- key change here
        .select_related("menu")
        .order_by("menu__name", "section", "name")
    )
    return render(request, "menus/my_menu.html", {"items": items})

from django.views.decorators.http import require_GET

@require_GET
def menu_sections_api(request):
    # Always return all possible section choices
    result = [
        {"value": value, "label": label}
        for value, label in MenuItem.SECTION_CHOICES
    ]
    return JsonResponse(result, safe=False)

def redirect_to_menu_editor(request, pk):
    return redirect('/menu-editor')


