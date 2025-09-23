from django import forms

class OrderForm(forms.Form):
    delivery_address = forms.CharField(max_length=255, required=False, label="Delivery Address")
    special_instructions = forms.CharField(widget=forms.Textarea, required=False, label="Special Instructions")
