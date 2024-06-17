from django import forms
from django.forms.utils import ErrorList

from .models import *


class ReviewBox(forms.ModelForm):
    RATING_TYPES = (
        (1, "★☆☆☆☆ (1/5)"), (2, "★★☆☆☆ (2/5)"), (3, "★★★☆☆ (3/5)"),
        (4, "★★★★☆ (4/5)"), (5, "★★★★★ (5/5)")
    )

    rating = forms.CharField(widget=forms.Select(choices=RATING_TYPES, attrs={
        'class': 'form-control',
        'name': 'education',

    }))

    review = forms.CharField(widget=forms.Textarea(attrs={
        "name": "product review",
        "placeholder": "Product Review?",
        'type': 'text',
        "rows": 3,
        "required": True
    }))

    class Meta:
        model = ProductReview
        fields = ["rating", "review"]


class AddressForm(forms.ModelForm):
    address = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={
        "name": "address",
        "placeholder": "Enter house / apartment number and street address",
        'type': 'text',
        "required": True,
        "id": "my-address"
    }))

    class Meta:
        model = Order
        fields = ["address"]


class ApplyCouponForm(forms.Form):
    code = forms.CharField(max_length=50, required=False, label=False)

