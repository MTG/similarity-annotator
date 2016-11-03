from django import forms
from django.core.exceptions import ValidationError
from .models import Exercise, Tier

import zipfile


class UploadForm(forms.Form):
    def clean_zip_file(self):
        zip_file = self.cleaned_data['zip_file']
        if not zipfile.is_zipfile(zip_file):
            raise ValidationError("The file type is not correct")

    zip_file = forms.FileField(
        label='Select a zip file with the sounds',
    )


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', })}


class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'size': '1'})}
