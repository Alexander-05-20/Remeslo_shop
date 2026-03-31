from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile
from django.utils.translation import gettext_lazy as _

class SignUpForm(UserCreationForm):
    username = forms.CharField(label=_("Имя пользователя"), max_length=150)
    email = forms.EmailField(label=_("Адрес электронной почты"),required=True, help_text='Обязательное. Введите корректный email.')
    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput)

    # добавляем поле номера телефона
    phone_number = forms.CharField(
        label=_("Номер телефона"),
        max_length=15,
        required=True,
        help_text='Обязательное. Начинается с + и содержит только цифры, например +79991234567.',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')  # добавляем в список полей

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот Email уже зарегистрирован.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        import re
        pattern = r'^\+\d+$'  # формат + и цифры
        if not re.match(pattern, phone):
            raise ValidationError('Введите номер в правильном формате, например +79991234567')
        return phone
    
    def save(self, commit=True):
        # Сначала вызываем оригинальный save(), чтобы создать пользователя
        user = super().save(commit=False)
        # Сохраняем пользователя
        if commit:
            user.save()
            # Создаем или получаем профиль и сохраняем номер
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user