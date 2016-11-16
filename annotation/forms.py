from django import forms
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from .models import Exercise, Tier

import zipfile


class ExerciseForm(forms.ModelForm):
    zip_file = forms.FileField(
        label='Select a zip file with the sounds',
    )

    class Meta:
        model = Exercise
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', })}

    def clean_name(self):
        exercise_name = self.cleaned_data["name"]
        try:
            Exercise.objects.get(name=exercise_name)
            raise forms.ValidationError("En exercise with that name already exists")
        except ObjectDoesNotExist:
            return exercise_name

    def clean_zip_file(self):
        zip_file = self.cleaned_data['zip_file']
        if not zipfile.is_zipfile(zip_file):
            raise ValidationError("The file type is not correct")


class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 8em;'})}
