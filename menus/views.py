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

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

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

class MenuCreateView(LoginRequiredMixin, CreateView):
    model = Menu
    form_class = MenuForm
    template_name = "menus/create_menu.html"
    success_url = reverse_lazy("menus:menu_list")  # Or use a detail view if you want to redirect to the new menu

    def form_valid(self, form):
        menu = form.save(commit=False)
        menu.owner = self.request.user
        menu.save()
        # If you want to handle MenuItemFormSet, you need to do it here
        formset = MenuItemFormSet(self.request.POST, instance=menu)
        if formset.is_valid():
            formset.save()
        else:
            return self.form_invalid(form)
        messages.success(self.request, f'Menu "{menu.name}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["restaurant_profile"], _ = RestaurantProfile.objects.get_or_create(user=user)
        context["profile"], _ = Profile.objects.get_or_create(user=user)
        if self.request.method == "POST":
            context["formset"] = MenuItemFormSet(self.request.POST)
        else:
            context["formset"] = MenuItemFormSet()
        context["title"] = "Create New Menu"
        return context
    
    
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

def public_menu_detail(request, slug: str, pk: int):
    # public endpoint: slug = owner's username
    owner = get_object_or_404(User, username=slug)
    menu = get_object_or_404(
        Menu.objects.prefetch_related("items"),
        pk=pk,
        owner=owner,
        is_active=True,
    )

    items_by_section = group_items_by_section(menu.items.all())

    context = {
        "menu": menu,
        "owner": owner,
        "items_by_section": dict(items_by_section),
        "is_owner": request.user.is_authenticated and menu.owner == request.user,
        "total_items": menu.items.count(),
    }
    return render(request, "restaurant_site/menu_detail.html", context)

class MenuUpdateView(LoginRequiredMixin, UpdateView):
    model = Menu
    form_class = MenuForm
    template_name = "menus/edit_menu.html"
    context_object_name = "menu"

    def get_queryset(self):
        # Only allow the owner to edit
        return Menu.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu = self.object
        if self.request.method == "POST":
            context["formset"] = MenuItemFormSet(self.request.POST, instance=menu)
        else:
            context["formset"] = MenuItemFormSet(instance=menu)
        context["title"] = f"Edit {menu.name}"
        return context

    def form_valid(self, form):
        menu = form.save()
        formset = MenuItemFormSet(self.request.POST, instance=menu)
        if formset.is_valid():
            formset.save()
            messages.success(self.request, f'Menu "{menu.name}" updated successfully!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy("menus:menu_detail", kwargs={"pk": self.object.pk})

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


