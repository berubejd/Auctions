from django import forms
from django.forms import ClearableFileInput, NumberInput, Select, Textarea, TextInput

from .models import Bid, Category, Comment, Listing, User


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("title", "description", "category", "image", "price")
        widgets = {
            "title": TextInput({"class": "form-control"}),
            "description": Textarea(
                {"class": "form-control", "rows": 10, "style": "resize: none;"}
            ),
            "image": ClearableFileInput({"class": "form-control"}),
            "price": NumberInput({"class": "form-control w-50"}),
            "category": Select({"class": "form-control"}),
        }
