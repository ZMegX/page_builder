from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Template, Webpage
from .forms import WebpageBuilderForm
import json

@login_required
def dashboard_home(request):
    templates = Template.objects.all()
    return render(request, "page_builder_app_create_page/select_template.html", {"templates": templates})

@login_required
def webpage_builder(request, template_slug):
    template = get_object_or_404(Template, slug=template_slug)
    if request.method == "POST":
        form = WebpageBuilderForm(request.POST)
        if form.is_valid():
            Webpage.objects.create(
                user=request.user,
                template=template,
                title=form.cleaned_data["title"],
                components_data=json.loads(form.cleaned_data["components_data"])
            )
            return redirect("my_webpages")
    else:
        form = WebpageBuilderForm()
    return render(request, "page_builder_app_create_page/webpage_builder.html", {"template": template, "form": form})

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