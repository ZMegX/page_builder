from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Template, Webpage
from .forms import WebpageBuilderForm, ComponentFormSet
import json

@login_required
def builder_home(request):
    templates = Template.objects.all()
    return render(request, "page_builder_app_create_page/select_template.html", {"templates": templates})

@login_required
def webpage_builder(request, template_slug):
    template = get_object_or_404(Template, slug=template_slug)
    if request.method == "POST":
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
            Webpage.objects.create(
                user=request.user,
                template=template,
                title=form.cleaned_data["title"],
                # add description/cover_image if your model supports
                components_data=components_data,
            )
            return redirect("my_webpages")
    else:
        form = WebpageBuilderForm()
        formset = ComponentFormSet()
    return render(request, "page_builder_app_create_page/webpage_builder.html", {
        "template": template,
        "form": form,
        "formset": formset,
    })

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