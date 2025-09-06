from django import forms
from django.forms import formset_factory

COMPONENT_TYPE_CHOICES = [
    ('header', 'Header'),
    ('text', 'Text'),
    ('image', 'Image'),
]

class ComponentForm(forms.Form):
    type = forms.ChoiceField(
        choices=COMPONENT_TYPE_CHOICES,
        label="Component Type",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Pick the type of component to add."
    )
    content = forms.CharField(
        label="Content / Image URL",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter text or image URL',
        }),
        help_text="The text, heading, or image URL for your component."
    )

ComponentFormSet = formset_factory(ComponentForm, extra=1, can_delete=True)

class WebpageBuilderForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        label="Page Title",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Give your page an awesome title...',
        }),
        help_text="The title of your new webpage. This will appear in the browser tab and as a heading."
    )

    description = forms.CharField(
        label="Short Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Describe your page for SEO and user context...',
        }),
        required=False,
        help_text="A short summary for your page (optional, for SEO and context)."
    )

    cover_image = forms.ImageField(
        label="Cover Image",
        required=False,
        help_text="Optional. Shown at the top of your page if provided."
    )

    address = forms.CharField(
        label="Restaurant Address",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_address',  # <-- important for JS
            'placeholder': 'Enter restaurant address...',
        }),
        required=False
    )
    latitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={'id': 'id_latitude'}),
        required=False
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={'id': 'id_longitude'}),
        required=False
    )
    