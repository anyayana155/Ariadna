from django import forms

from apps.bookings.models import BookingRequest
from apps.places.models import Place


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data if d]
            return result
        if data:
            return [single_file_clean(data, initial)]
        return []


class DashboardBookingUpdateForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['status', 'admin_comment', 'alternative_text']
        widgets = {
            'admin_comment': forms.Textarea(attrs={'rows': 4}),
            'alternative_text': forms.Textarea(attrs={'rows': 4}),
        }


class DashboardPlaceForm(forms.ModelForm):
    external_image_urls = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Каждая ссылка на фото с новой строки'
        }),
        label='Внешние ссылки на изображения'
    )
    upload_images = MultipleFileField(
        required=False,
        label='Загрузить изображения'
    )

    class Meta:
        model = Place
        fields = [
            'title',
            'category',
            'short_description',
            'full_description',
            'address',
            'metro',
            'average_check',
            'atmosphere',
            'tags_text',
            'source',
            'is_published',
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.HiddenInput(),
        }
