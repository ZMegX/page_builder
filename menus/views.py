from django.shortcuts import render, get_object_or_404, redirect
from .models import Menu
from .forms import MenuItemFormSet
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseForbidden


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ["name", "description", "is_active"]

@login_required
def create_menu(request):
    try:
        # ✅ follow the User → Profile → RestaurantProfile chain
        restaurant_profile = request.user.profile.restaurant_details
    except AttributeError:
        return HttpResponseForbidden("You must be a restaurant to create menus.")

    if request.method == "POST":
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.restaurant = restaurant_profile  # attach restaurant profile
            menu.save()
            return redirect("menus:edit_menu_items", menu_id=menu.id)
    else:
        form = MenuForm()

    return render(request, "menus/create_menu.html", {"form": form})


def edit_menu_items(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)

    if request.method == "POST":
        formset = MenuItemFormSet(request.POST, queryset=menu.items.all())
        if formset.is_valid():
            items = formset.save(commit=False)
            
            # attach menu to new items
            for item in items:
                item.menu = menu
                item.save()

            # handle deleted forms
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect("menu_detail", menu_id=menu.id)
    else:
        formset = MenuItemFormSet(queryset=menu.items.all())

    return render(request, "menus/edit_menu_items.html", {
        "menu": menu,
        "formset": formset,
    })



def menu_detail(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    items = menu.items.all()  # because of related_name="items"

    return render(request, "menus/menu_detail.html", {
        "menu": menu,
        "items": items,
    })
