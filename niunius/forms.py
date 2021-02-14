from django import forms
from django.contrib.auth.models import User

from .models import Article, ArticleComment


# class LoginForm(forms.Form):
#     username = forms.CharField(label="Nazwa użytkownika")
#     password = forms.CharField(widget=forms.PasswordInput, label="Hasło")


class ArticleForm(forms.ModelForm):
    photos = forms.ImageField(
        label="",
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
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
