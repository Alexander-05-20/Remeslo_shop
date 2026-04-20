from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile
from django.utils.translation import gettext_lazy as _
import re

class SignUpForm(UserCreationForm):
    # Новые поля:
    first_name = forms.CharField(
        label=_("Имя"),
        max_length=15,
        required=True,
        help_text='Максимум 15 символов, без цифр.',
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        max_length=15,
        required=True,
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
        help_text='Начинается с +7 и содержит максимум 12 цифр без букв.',
        widget=forms.TextInput(attrs={
        'placeholder': '+79991234567'
        })
    )
    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if re.search(r'\d', first_name):
            raise ValidationError('Имя не должно содержать цифр.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if re.search(r'\d', last_name):
            raise ValidationError('Фамилия не должна содержать цифр.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот Email уже зарегистрирован.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Проверка формата +7 и максимум 12 цифр (например, +79991234567)
        pattern = r'^\+7\d{10}$'  # начиная с +7
        if not re.match(pattern, phone):
            raise ValidationError('Введите номер в правильном формате, например +79991234567')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # можно установить имя и фамилию прямо так, или оставить в профиле
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user
    
