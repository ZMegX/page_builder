from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from users.models import Profile, Address, RestaurantProfile

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
    # Visible search input for Google Places Autocomplete (non-model)
    address_search = forms.CharField(
        required=False,
        label='Restaurant Address',
        widget=forms.TextInput(attrs={
            'id': 'id_address',
            'class': 'form-control',
            'placeholder': 'Start typing address...',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Address
        fields = [
            'address_search',  # non-model field to render the search input
            'street',
            'city',
            'state',
            'country',
            'zipcode',
            'latitude',
            'longitude',
        ]
        widgets = {
            # Keep components hidden; JS fills them
            'street': forms.HiddenInput(attrs={'id': 'id_street'}),
            'city': forms.HiddenInput(attrs={'id': 'id_city'}),
            'state': forms.HiddenInput(attrs={'id': 'id_state'}),
            'country': forms.HiddenInput(attrs={'id': 'id_country'}),
            'zipcode': forms.HiddenInput(attrs={'id': 'id_zipcode'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
        }

    def clean(self):
        cleaned = super().clean()
        street = cleaned.get('street')
        city = cleaned.get('city')
        country = cleaned.get('country')
        if not street or not city or not country:
            raise forms.ValidationError("Please select a full address to populate street, city, and country.")
        return cleaned


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

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

# Custom Set Password Form (for password reset/change flows)
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

