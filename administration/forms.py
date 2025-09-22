from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import BlogPost


class EditBalanceForm(forms.Form):
    new_balance = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget()
    )

    class Meta:
        model = BlogPost
        fields = ["title", "image", "content"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter blog title"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }
