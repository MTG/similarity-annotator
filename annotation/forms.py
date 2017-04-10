from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from multiupload.fields import MultiFileField

from .models import Tier, DataSet


class TierForm(forms.ModelForm):
    dimensions = forms.CharField(label='Dimensions', required=False)

    class Meta:
        model = Tier
        fields = ['name', 'parent_tier', 'special_parent_tier', 'point_annotations']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 8em;',
                                                  'placeholder': 'Name'}),
                   'parent_tier': forms.Select(attrs={'class': 'form-control', 'style': 'width: 8em;',
                                                      'placeholder': 'parent_tier'}),
                   'special_parent_tier': forms.Select(attrs={'class': 'form-control', 'style': 'width: 8em;',
                                                       'placeholder': 'special_parent_tier'}),
                   'point_annotations': forms.CheckboxInput()}

    def __init__(self, *args, **kwargs):
        parent_ids = kwargs.get('parent_tier_ids', None)
        if 'parent_tier_ids' in kwargs:
            del kwargs['parent_tier_ids']
        super(TierForm, self).__init__(*args, **kwargs)
        if parent_ids:
            self.fields['parent_tier'].queryset = Tier.objects.filter(id__in=parent_ids)
            self.fields['special_parent_tier'].queryset = Tier.objects.filter(id__in=parent_ids)
        if self.instance:
            self.fields['dimensions'].initial = ', '.join(self.instance.similarity_keys)

    def clean_dimensions(self):
        if self.cleaned_data['dimensions']:
            return [s for s in self.cleaned_data['dimensions'].split(',')]
        else:
            return None

    def is_valid(self):
        valid = super(TierForm, self).is_valid()

        if not valid:
            return valid

        if self.cleaned_data['dimensions']:
            return True
        else:
            self._errors['invalid_dimensions'] = "You should provide at least one dimension"
            False


class UploadFileForm(forms.Form):
    def validate_audio_file(audiofileslist):
        for audiofile in audiofileslist:
            content_type = audiofile.content_type
            if not content_type.startswith("audio"):
                raise ValidationError("%(file_name)s is not an audio file") % {'file_name': audiofile.name}
        return audiofileslist

    audiofile = MultiFileField(min_num=1, max_num=100, validators=[validate_audio_file])


class DataSetForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ['name']
