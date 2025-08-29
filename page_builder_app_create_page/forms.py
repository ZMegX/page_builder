from django import forms

class WebpageBuilderForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        help_text="The title of your new webpage. This will appear in the browser tab and as a heading."
    )
    components_data = forms.CharField(
        widget=forms.HiddenInput(),
        help_text="The web components you add below will be stored here as JSON."
    )