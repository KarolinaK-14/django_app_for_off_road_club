import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import SelectDateWidget
from django.utils import timezone

from .models import Article, ArticleComment, Order, CarService


class UserForm(UserCreationForm):
    """
    The form that extends the built-in UserCreationForm with the following fields:
    email, first name and last name.
    """

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
        user = super(UserForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class MessageForm(forms.Form):
    """The form that allows users send an e-mail message."""

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
    """Raise the error if the given date has already passed."""
    if visit_date < datetime.date.today():
        raise ValidationError("Ale to już było! Wybierz datę z przyszłości")


class VisitForm(forms.Form):
    """The form that allows users to book a visit to the car service station."""

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
    """
    The form that allows users adding new Article object.
    Additional "photos" field serves to add photos to ArticlePhoto model.
    """

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
            "title": forms.TextInput(attrs={"placeholder": "Tytuł"}),
            "content": forms.Textarea(attrs={"placeholder": "Opis"}),
        }


class ArticleCommentForm(forms.ModelForm):
    """The form that allows users adding comments to articles."""

    class Meta:
        model = ArticleComment
        fields = ["text"]
        labels = {"text": ""}


class BuyerForm(forms.ModelForm):
    """The one of order forms for personal data of the buyer who is the registered user."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {"first_name": "Imię", "last_name": "Nazwisko", "email": "E-mail"}


class GuestForm(forms.Form):
    """
    The one of order forms for personal data of the buyer
    who wants to place an order as a guest, without registration.
    """

    guest_first_name = forms.CharField(widget=forms.TextInput(), label="Imię")
    guest_last_name = forms.CharField(widget=forms.TextInput(), label="Nazwisko")
    guest_email = forms.EmailField(widget=forms.EmailInput(), label="E-mail")


class DeliveryForm(forms.Form):
    """
    The one of order forms to choose delivery method.
    Default choice: "Kurier"
    """

    delivery_method = forms.ChoiceField(
        choices=[("Kurier", "Kurier"), ("Odbiór własny", "Odbiór własny")],
        widget=forms.RadioSelect(),
        label="",
        initial="Kurier",
    )


class PaymentForm(forms.Form):
    """
    The one of order forms to choose payment method.
    Default choice: "Przelew"
    """

    payment_method = forms.ChoiceField(
        choices=[
            ("Przelew", "Przelew"),
            ("Płatność przy odbiorze", "Płatność przy odbiorze"),
        ],
        widget=forms.RadioSelect(),
        label="",
        initial="Przelew",
    )


class OrderForm(forms.ModelForm):
    """The one of order forms for address data."""

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
