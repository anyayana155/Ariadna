from django import forms
from .models import FavoriteFolder


class FavoriteFolderForm(forms.ModelForm):
    class Meta:
        model = FavoriteFolder
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Например: Кофейни для работы'
            })
        }


class AddToFolderForm(forms.Form):
    folder = forms.ModelChoiceField(
        queryset=FavoriteFolder.objects.none(),
        required=False,
        empty_label='Выберите папку'
    )
    new_folder_name = forms.CharField(
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={
            'placeholder': 'Или создай новую папку'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['folder'].queryset = FavoriteFolder.objects.filter(user=user).order_by('name')
