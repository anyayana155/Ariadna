from django import forms
from .models import PreferenceProfile


class PreferenceProfileForm(forms.ModelForm):
    class Meta:
        model = PreferenceProfile
        fields = [
            'budget',
            'atmosphere',
            'purpose',
            'company_type',
            'distance',
            'extra_text',
        ]
        widgets = {
            'extra_text': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Например: люблю тихие места для работы, важны розетки, не люблю слишком шумные заведения...'
            })
        }