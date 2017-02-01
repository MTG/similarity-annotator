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
        fields = ['name', 'reference_pitch_sound']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', })}

    def clean_zip_file(self):
        zip_file = self.cleaned_data['zip_file']
        if not zipfile.is_zipfile(zip_file):
            raise ValidationError("The file type is not correct")

    def __init__(self, *args, **kwargs):
        super(ExerciseForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True


class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['name', 'parent_tier']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 8em;',
                                                  'placeholder': 'Name'}),
                   'parent_tier': forms.Select(attrs={'class': 'form-control', 'style': 'width: 8em;',
                                                      'placeholder': 'parent_tier'})}

    def __init__(self, *args, **kwargs):
        ids = kwargs.get('parent_tier_ids', None)
        if 'parent_tier_ids' in kwargs:
            del kwargs['parent_tier_ids']
        super(TierForm, self).__init__(*args, **kwargs)
        if ids:
            self.fields['parent_tier'].queryset = Tier.objects.filter(id__in=ids)

