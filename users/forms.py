from django import forms
from .models import Profile, Address
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm #Inheritance Relationship
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'company_name',
            'image',
            'email',
            'phone_number',
            'description',
            'cuisine_type',
            'established_year',
            'registration_number',
            'tax_id',
            'website',
            'capacity',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'street',
            'city',
            'state',
            'country',
            'zipcode',
            'latitude',
            'longitude',
        ]



class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
        
class UserRegisterForm(UserCreationForm):
  email = forms.EmailField()

  class Meta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'company_name', 'image', 'phone_number', 'description',
            'cuisine_type', 'established_year', 'registration_number',
            'tax_id', 'website', 'capacity'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False



class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom attributes here, e.g., placeholders
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})