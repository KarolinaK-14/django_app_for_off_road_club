import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import SelectDateWidget
from django.utils import timezone

from .models import Article, ArticleComment, Order, CarService


class RegisterForm(UserCreationForm):
    """A form that creates a new user."""

    email = forms.EmailField(label="E-mail")
    first_name = forms.CharField(label="Imię")
    last_name = forms.CharField(label="Nazwisko")

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password1",
            "password2",
        ]

        labels = {"username": "Nazwa użytkownika"}

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class MessageForm(forms.Form):
    """A form that allows a user send an email message."""

    message_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Twoje imię"})
    )
    message_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Twój e-mail"})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Twoja wiadomość", "rows": "6"})
    )


def validate_date(visit_date):
    """Check if the given date is in the past. If so, raise the error."""

    if visit_date < datetime.date.today():
        raise ValidationError("Data nie może być z przeszłości")


class VisitForm(forms.Form):
    """A form that allows a user book a visit."""

    client_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Twoje imię"}), label=""
    )
    client_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Twój e-mail"}), label=""
    )
    client_phone = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Twój numer telefonu"}),
        label="",
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Podaj numer telefonu w poprawnym formacie, np. +999999999",
            )
        ],
    )
    service = forms.ModelChoiceField(CarService.objects, label="Usługa")
    visit_date = forms.DateField(
        widget=SelectDateWidget(),
        label="Dzień",
        validators=[validate_date],
        initial=timezone.now(),
    )
    visit_time = forms.ChoiceField(
        choices=[
            ("", "------------------"),
            ("Ranny ptaszek (7:00 - 12:00)", "Ranny ptaszek (7:00 - 12:00)"),
            ("Jak człowiek (13:00 - 18:00)", "Jak człowiek (13:00 - 18:00)"),
            ("Nocny marek (19:00 - 22:00", "Nocny marek (19:00 - 22:00"),
        ],
        label="Przedział czasowy",
    )


class ArticleForm(forms.ModelForm):
    photos = forms.ImageField(
        label="",
        widget=forms.ClearableFileInput(
            attrs={"multiple": True, "style": "display: none"}
        ),
        required=False,
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


class BuyerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {"first_name": "Imię", "last_name": "Nazwisko", "email": "E-mail"}


class GuestForm(forms.Form):
    guest_first_name = forms.CharField(widget=forms.TextInput(), label="Imię")
    guest_last_name = forms.CharField(widget=forms.TextInput(), label="Nazwisko")
    guest_email = forms.EmailField(widget=forms.EmailInput(), label="E-mail")


class DeliveryForm(forms.Form):
    delivery_method = forms.ChoiceField(
        choices=[("Kurier", "Kurier"), ("Odbiór własny", "Odbiór własny")],
        widget=forms.RadioSelect(),
        label="",
    )


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[
            ("Przelew", "Przelew"),
            ("Płatność przy odbiorze", "Płatność przy odbiorze"),
        ],
        widget=forms.RadioSelect(),
        label="",
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "address_street",
            "address_zipcode",
            "address_city",
            "address_country",
        ]
        labels = {
            "address_city": "Miasto",
            "address_zipcode": "Kod pocztowy",
            "address_street": "Ulica",
            "address_country": "Kraj",
        }
        widgets = {
            "address_zipcode": forms.TextInput(attrs={"placeholder": "XX-XXX"}),
            "address_country": forms.TextInput(attrs={"value": "Polska"}),
        }
