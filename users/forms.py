from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from users.models import Profile, RestaurantProfile
from locations.models import UserAddress

# Profile Create/Edit Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'image',
        ]
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Profile Update Form (same as ProfileForm, can be omitted if not differing)
ProfileUpdateForm = ProfileForm

# Address Create/Edit Form
class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['formatted_address', 'latitude', 'longitude']


class RestaurantDetailsForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = [
            'name',
            'cuisine_type',
            'registration_number',
            'phone_number',
            'logo',
            
        ]
# User Registration Form (extend as needed)
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant Owner'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "role")

# Custom Set Password Form (for password reset/change flows)
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

