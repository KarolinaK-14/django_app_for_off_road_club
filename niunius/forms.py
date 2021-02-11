from django import forms
from .models import Article, ArticleComment


class LoginForm(forms.Form):
    username = forms.CharField(label="Nazwa użytkownika")
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content"]
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
