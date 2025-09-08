from django import forms
from django.forms import inlineformset_factory
from .models import RestaurantProfile, Address, SocialLink, OpeningHour

DAYS_OF_WEEK = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]

class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = ["name", "cuisine_type", "registration_number", "phone_number", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Restaurant name"}),
            "cuisine_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cuisine type"}),
            "registration_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Registration number"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+1 555 555 5555"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*", "id": "id_logo_input"}),
        }

class AddressForm(forms.ModelForm):
    address_search = forms.CharField(
        required=False,
        label="Restaurant Address",
        widget=forms.TextInput(attrs={
            "id": "id_address",
            "class": "form-control",
            "placeholder": "Start typing an address...",
            "autocomplete": "off"
        })
    )

    class Meta:
        model = Address
        fields = [
            "address_search",
            "street", "city", "state", "country", "zipcode",
            "latitude", "longitude",
        ]
        widgets = {
            "street": forms.HiddenInput(attrs={"id": "id_street"}),
            "city": forms.HiddenInput(attrs={"id": "id_city"}),
            "state": forms.HiddenInput(attrs={"id": "id_state"}),
            "country": forms.HiddenInput(attrs={"id": "id_country"}),
            "zipcode": forms.HiddenInput(attrs={"id": "id_zipcode"}),
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("street") or not cleaned.get("city") or not cleaned.get("country"):
            raise forms.ValidationError("Please select a full address from the suggestions (street, city, country).")
        return cleaned

class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ["name", "url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Instagram"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
        }

class OpeningHourForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(choices=DAYS_OF_WEEK, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = OpeningHour
        fields = ["day_of_week", "open_time", "close_time"]
        widgets = {
            "open_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "close_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        open_t = cleaned.get("open_time")
        close_t = cleaned.get("close_time")
        if open_t and close_t and close_t <= open_t:
            raise forms.ValidationError("Close time must be after open time.")
        return cleaned

SocialLinkFormSet = inlineformset_factory(
    parent_model=RestaurantProfile,
    model=SocialLink,
    form=SocialLinkForm,
    extra=1,
    can_delete=True,
)

OpeningHourFormSet = inlineformset_factory(
    parent_model=RestaurantProfile,
    model=OpeningHour,
    form=OpeningHourForm,
    extra=1,
    can_delete=True,
)