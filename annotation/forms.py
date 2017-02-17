from django import forms

from .models import Tier



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

