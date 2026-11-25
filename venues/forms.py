from django import forms
from django.core.exceptions import ValidationError

from .models import Venue

MAX_PHOTO_SIZE = 2 * 1024 * 1024


class VenuePhotoForm(forms.ModelForm):
    """Загрузка фото площадки."""

    class Meta:
        model = Venue
        fields = ["photo"]
        widgets = {
            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}),
        }

    def clean_photo(self):
        # ImageField уже проверил, что файл — изображение; ограничим размер.
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > MAX_PHOTO_SIZE:
            raise ValidationError("Файл больше 2 МБ.")
        return photo
