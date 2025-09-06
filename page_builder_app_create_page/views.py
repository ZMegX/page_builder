from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Template, Webpage, PageElement
from .forms import WebpageBuilderForm, ComponentFormSet
from django.http import JsonResponse
from django.conf import settings
import requests
from django.urls import reverse  

def geocode_address(address):
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

@login_required
def builder_home(request):
    templates = Template.objects.all()
    return render(request, "page_builder_app_create_page/select_template.html", {"templates": templates})

@login_required
def webpage_builder(request, template_slug):
    template = get_object_or_404(Template, slug=template_slug)
    edit_mode = request.user.is_authenticated

    if edit_mode and request.method == "POST":
        form = WebpageBuilderForm(request.POST, request.FILES)
        formset = ComponentFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            components_data = [
                {
                    "type": comp_form.cleaned_data["type"],
                    "content": comp_form.cleaned_data["content"]
                }
                for comp_form in formset
                if comp_form.cleaned_data and not comp_form.cleaned_data.get('DELETE', False)
            ]
            address = form.cleaned_data.get('address')
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')
            if address and (not lat or not lng):
                lat, lng = geocode_address(address)
            Webpage.objects.create(
                user=request.user,
                template=template,
                title=form.cleaned_data["title"],
                components_data=components_data,
                address=address,
                latitude=lat,
                longitude=lng,
            )
            return redirect(reverse('page_builder_app_create_page:my_webpages'))
    else:
        form = WebpageBuilderForm() if edit_mode else None
        formset = ComponentFormSet() if edit_mode else None

    return render(request, "page_builder_app_create_page/webpage_builder.html", {
        "template": template,
        "form": form,
        "formset": formset,
        "edit_mode": edit_mode,
    })
    

@login_required
@require_POST
def save_page_element(request, webpage_id):
    webpage = get_object_or_404(Webpage, id=webpage_id, user=request.user)

    element_type = request.POST.get("element_type")
    order = request.POST.get("order", 0)

    element = PageElement.objects.create(
        webpage=webpage,
        element_type=element_type,
        order=order
    )

    if element_type == "text":
        element.content = request.POST.get("content", "")

    element.save()

    return JsonResponse({"status": "ok", "id": element.id})



# Example in your view
def save_webpage(request):
    if request.method == "POST":
        form = WebpageBuilderForm(request.POST, request.FILES)
        if form.is_valid():
            address = form.cleaned_data['address']
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')

            # If no lat/lng from client, fallback to Geocoding
            if not lat or not lng:
                lat, lng = geocode_address(address)

            # Save webpage
            Webpage.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                cover_image=form.cleaned_data['cover_image'],
                address=address,
                latitude=lat,
                longitude=lng
            )

@login_required
def my_webpages(request):
    pages = Webpage.objects.filter(user=request.user)
    return render(request, "page_builder_app_create_page/my_webpages.html", {"pages": pages})

def render_webpage(request, webpage_id):
    page = get_object_or_404(Webpage, id=webpage_id)
    template_slug = page.template.slug
    return render(request, f"page_builder_app_create_page/render_templates/{template_slug}.html", {
        "webpage": page,
        "components": page.components_data,
    })