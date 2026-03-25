from django import forms

from apps.bookings.models import BookingRequest
from apps.places.models import Place


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.setdefault('accept', 'image/*')
        super().__init__(attrs)


class MultipleImageField(forms.FileField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data if item]
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
    upload_images = MultipleImageField(
        required=False,
        label='Добавить фотографии'
    )

    class Meta:
        model = Place
        fields = [
            'title',
            'slug',
            'category',
            'short_description',
            'full_description',
            'address',
            'metro',
            'average_check',
            'atmosphere',
            'tags_text',
            'is_published',
        ]
        labels = {
            'tags_text': 'Теги / ключевые слова',
        }
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.HiddenInput(),
        }

    def clean_slug(self):
        slug = (self.cleaned_data.get('slug') or '').strip()
        if not slug:
            raise forms.ValidationError('Укажи slug латиницей.')
        return slug
