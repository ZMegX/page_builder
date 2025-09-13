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
            })
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
        fields = ["section", "name", "price", "ingredients", "image"]
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
            })
        }
        labels = {
            'section': 'Category',
            'name': 'Item Name',
            'price': 'Price ($)',
            'ingredients': 'Ingredients',
            'image': 'Item Image'
        }

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

# Optimized FormSet with better defaults
MenuItemFormSet = inlineformset_factory(
    Menu, 
    MenuItem, 
    form=MenuItemForm, 
    extra=2,  # Reduced from 3 to 2 for cleaner UI
    can_delete=True,
    min_num=1,  # Require at least 1 menu item
    validate_min=True,
    max_num=20,  # Prevent too many items at once
    validate_max=True
)

# Custom formset class for additional validation
class CustomMenuItemFormSet(MenuItemFormSet):
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

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'ingredients', 'price', 'section', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name...'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Describe your delicious item...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'section': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default availability to True
        if not self.instance.pk:
            self.fields['is_available'].initial = True