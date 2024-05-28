from django import forms
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
