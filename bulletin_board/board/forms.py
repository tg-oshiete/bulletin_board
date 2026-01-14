from django import forms
from .models import Ad, Response

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'content', 'category', 'image', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок объявления'
        }),
        'content': forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Подробно опишите ваше объявление'
        }),
        'category':forms.Select(attrs={
            'class': 'form-select'
        }),
        'image': forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        'file': forms.FileInput(attrs={
            'class': 'form-control'
        })}
        labels = {
            'title':'Заголовок',
            'content':'Содержание',
            'category':'Категория',
            'image':'Изображение',
            'file':'Прикрепленный файл'
        }
        help_texts = {
            'image': 'Загрузите изображение для вашего объявления (необязательно)',
            'file': 'Прикрепите дополнительный файл (необязательно)'
        }


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите ваш отклик...',
                'style': 'resize: vertical; min-height: 120px;'
            }),
        }
        labels = {
            'text': 'Текст отклика',
        }

class ResponseFilterForm(forms.Form):
    FILTER_CHOICES = [
        ('all', 'Все отклики'),
        ('accepted', 'Принятые'),
        ('pending', 'Ожидающие'),
        ('my', 'Мои отклики'),
    ]

    filter_type = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Поиск по тексту или объявлению...'
        })
    )