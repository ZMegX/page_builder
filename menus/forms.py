from django import forms
from django.forms import modelformset_factory
from .models import MenuItem


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["name", "description", "price", "category", "is_available"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 1, "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


MenuItemFormSet = modelformset_factory(
    MenuItem,
    form=MenuItemForm,
    extra=1,  # one blank form by default
    can_delete=True  # allow user to delete rows
)
