from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from harvoldsite import consts


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, label="EMAIL", error_messages={"exists": "Email already in use!"})
    password1 = forms.CharField(
        label='PASSWORD',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )
    password2 = forms.CharField(
        label='CONFIRM PW',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "USERNAME",
        }

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError(self.fields["email"].error_messages["exists"])
        return self.cleaned_data["email"]


class TrainerSelectForm(forms.Form):
    trainer = forms.ChoiceField(
        choices=consts.TRAINER_CHOICES,
        label="Choose your trainer"
    )


class StarterChoiceForm(forms.Form):
    pokemon = forms.ChoiceField(
        choices=consts.STARTER_CHOICES,
        label="Choose your starter"
    )