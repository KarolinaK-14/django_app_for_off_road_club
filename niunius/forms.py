from django import forms
from django.contrib.auth.models import User
from .models import Article, ArticleComment, Order


class BuyerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {"first_name": "imię", "last_name": "nazwisko", "email": "email"}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "address_country",
            "address_street",
            "address_zipcode",
            "address_city",
        ]
        labels = {
            "address_city": "miasto",
            "address_zipcode": "kod pocztowy",
            "address_street": "ulica",
            "address_country": "kraj",
        }
        widgets = {
            "address_zipcode": forms.TextInput(attrs={"placeholder": "XX-XXX"}),
            "address_country": forms.TextInput(attrs={"value": "Polska"}),
        }


class ArticleForm(forms.ModelForm):
    photos = forms.ImageField(
        label="", widget=forms.ClearableFileInput(attrs={"multiple": True})
    )

    class Meta:
        model = Article
        fields = ["title", "content", "photos"]
        labels = {"title": "", "content": ""}
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "nazwa wydarzenia"}),
            "content": forms.Textarea(attrs={"placeholder": "opis"}),
        }


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ["text"]
        labels = {"text": ""}
