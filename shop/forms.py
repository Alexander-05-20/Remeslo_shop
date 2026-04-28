from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile
from django.utils.translation import gettext_lazy as _
import re
from .validators import validate_name, validate_surname, validate_phone

class SignUpForm(UserCreationForm):
    # Новые поля:
    first_name = forms.CharField(
        label=_("Имя"),
        max_length=15,
        required=True,
        validators=[validate_name],
        help_text='Максимум 15 символов, без цифр.',
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        max_length=15,
        required=True,
        validators=[validate_surname],
        help_text='Максимум 15 символов, без цифр.',
    )
    email = forms.EmailField(
        label=_("Адрес электронной почты"),
        required=True,
        help_text='Обязательное. Введите корректный email.',
        widget=forms.TextInput(attrs={
        'placeholder': 'username@example.com'
        })
    )
    phone_number = forms.CharField(
        label=_("Номер телефона"),
        max_length=12,
        required=True,
        validators=[validate_phone],
        help_text='Начинается с +7 и содержит максимум 12 цифр без букв.',
        widget=forms.TextInput(attrs={'placeholder': '+79991234567'})
    )
    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user
    
