from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Profile, Address

# Profile Create/Edit Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'company_name', 'image', 'email', 'phone_number', 'description',
            'cuisine_type', 'established_year', 'registration_number',
            'tax_id', 'website', 'capacity',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image optional
        self.fields['image'].required = False

# Profile Update Form (same as ProfileForm, can be omitted if not differing)
ProfileUpdateForm = ProfileForm

# Address Create/Edit Form
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'street', 'city', 'state', 'country', 'zipcode',
            'latitude', 'longitude',
        ]

# User Registration Form (extend as needed)
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

# User Update Form
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Custom Set Password Form (for password reset/change flows)
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})