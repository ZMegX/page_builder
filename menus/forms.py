from django import forms
from .models import Menu, MenuItem
from django.forms import inlineformset_factory

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ["name", "photo", "is_active"]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter menu name...',
                'maxlength': '100'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            
        }
        labels = {
            'name': 'Menu Name',
            'photo': 'Menu Photo',
            'is_active': 'Active Menu'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 3:
            raise forms.ValidationError("Menu name must be at least 3 characters long.")
        return name.strip() if name else name

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["section", "name", "price", "ingredients", "image", "is_available", "popular_items"]
        widgets = {
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Item name...',
                'maxlength': '80'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List main ingredients...',
                'rows': 2,
                'maxlength': '200'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'popular_items': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'section': 'Category',
            'name': 'Item Name',
            'price': 'Price ($)',
            'ingredients': 'Ingredients',
            'image': 'Item Image',
            'is_available': 'Available',
            'popular_items': 'Mark as Popular'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default availability to True
        if not self.instance.pk:
            self.fields['is_available'].initial = True

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        if price is not None and price > 9999.99:
            raise forms.ValidationError("Price cannot exceed $9,999.99.")
        return price

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise forms.ValidationError("Item name must be at least 2 characters long.")
        return name.strip() if name else name

# Custom formset class for additional validation
from django.forms import BaseInlineFormSet
class CustomMenuItemFormSet(BaseInlineFormSet):
    def clean(self):
        """
        Add custom validation for the entire formset
        """
        if any(self.errors):
            return
        sections = []
        names = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                section = form.cleaned_data.get('section')
                name = form.cleaned_data.get('name')
                if section:
                    sections.append(section)
                if name:
                    names.append(name.lower())
        # Check for duplicate item names
        if len(names) != len(set(names)):
            raise forms.ValidationError("Menu items must have unique names.")
        # Ensure at least one item per menu
        if not sections:
            raise forms.ValidationError("Menu must have at least one item.")

# Use the custom formset
MenuItemFormSet = inlineformset_factory(
    Menu, 
    MenuItem, 
    form=MenuItemForm,
    formset=CustomMenuItemFormSet,
    extra=2,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=20,
    validate_max=True
)