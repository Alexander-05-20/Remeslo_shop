import re
from django.core.exceptions import ValidationError

def validate_name(value):
    if len(value) > 15:
        raise ValidationError('Длина должна быть не более 15 символов.')
    if not re.match(r'^[А-Яа-яЁё]+$', value):
        raise ValidationError('Имя должно содержать только буквы без цифр.')

def validate_surname(value):
    if len(value) > 15:
        raise ValidationError('Длина должна быть не более 15 символов.')
    if not re.match(r'^[А-Яа-яЁё]+$', value):
        raise ValidationError('Фамилия должна содержать только буквы без цифр.')

def validate_phone(value):
    if not re.match(r'^\+7\d{10}$', value):
        raise ValidationError('Телефон должен начинаться с +7 и содержать максимум 12 цифр без букв.')