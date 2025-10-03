from django import forms
from django.forms import inlineformset_factory
from .models import RestaurantProfile, SocialLink, OpeningHour
from users.models import Review

DAYS_OF_WEEK = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]

# restaurant details form
class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = [
            "name",
            "cuisine_type",
            "registration_number",
            "phone_number",
            "logo",
            "theme_choice",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Restaurant name"}),
            "cuisine_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cuisine type"}),
            "registration_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Registration number"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+1 555 555 5555"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*", "id": "id_logo_input"}),
            "theme_choice": forms.Select(attrs={"class": "form-select"}),
        }

# hero section form
class HeroForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = [
            "hero_headline",
            "hero_description",
            "hero_image",
        ]
        widgets = {
            "hero_headline": forms.TextInput(attrs={"class": "form-control", "placeholder": "Main headline"}),
            "hero_description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Main description", "rows": 2}),
            "hero_image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

# about section form
class AboutForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = [
            "about_headline",
            "about_description",
            "about_image",
            "about_highlight",
        ]
        widgets = {
            "about_headline": forms.TextInput(attrs={"class": "form-control", "placeholder": "About headline"}),
            "about_description": forms.Textarea(attrs={"class": "form-control", "placeholder": "About description", "rows": 3}),
            "about_image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "about_highlight": forms.TextInput(attrs={"class": "form-control", "placeholder": "About highlight: say a fun fact or quote"}),
        }
    
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
    is_closed = forms.BooleanField(required=False, label="Closed", widget=forms.CheckboxInput(attrs={"class": "is-closed-checkbox"}))

    class Meta:
        model = OpeningHour
        fields = ["day_of_week", "is_closed", "open_time", "close_time"]
        widgets = {
            "open_time": forms.TimeInput(attrs={"type": "time", "class": "open-time-input form-control"}),
            "close_time": forms.TimeInput(attrs={"type": "time", "class": "close-time-input form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        is_closed = cleaned.get("is_closed")
        open_t = cleaned.get("open_time")
        close_t = cleaned.get("close_time")
        if not is_closed:
            if not open_t or not close_t:
                raise forms.ValidationError("Please enter both open and close times or mark as closed.")
            if close_t <= open_t:
                raise forms.ValidationError("Close time must be after open time.")
        else:
            cleaned["open_time"] = None
            cleaned["close_time"] = None
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
    extra=3,
    max_num=7,
    can_delete=False,
)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'reviewer_name']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f"{i} Stars") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review...'}),
            'reviewer_name': forms.TextInput(attrs={'placeholder': 'Your name (optional)'}),
        }

class ReviewReplyForm(forms.ModelForm):
    """Form for restaurant owners to reply to reviews"""
    class Meta:
        model = Review
        fields = ['owner_reply']
        widgets = {
            'owner_reply': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Write your response to this review...'
            }),
        }
        labels = {
            'owner_reply': 'Your Reply'
        }