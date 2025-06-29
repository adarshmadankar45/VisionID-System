from django import forms
from .models import Criminal

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ImageUploadForm(forms.Form):
    images = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
            'multiple': True,
            'class': 'file-input'
        }),
        label='Upload Images for Matching'
    )

class CriminalForm(forms.ModelForm):
    images = MultipleFileField(required=False, label='Upload Images (Multiple)')
    age = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        label='Age (Auto-calculated)'
    )

    class Meta:
        model = Criminal
        fields = ['first_name', 'middle_name', 'last_name', 'dob', 'age', 'gender']
        widgets = {
            'dob': forms.DateInput(attrs={
                'type': 'date',
                'onchange': 'calculateAge(this.value)'
            }),
            'gender': forms.RadioSelect()
        }

class CriminalImageSearchForm(forms.Form):
    image = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
            'multiple': True,
            'class': 'form-control'
        }),
        label='Search by Images',
        help_text='Upload multiple photos to find matching criminal records (JPEG, PNG)'
    )