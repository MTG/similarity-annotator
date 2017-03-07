from django import forms

from .models import Tier


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
        return [s.strip() for s in self.cleaned_data['dimensions'].split(',')]

