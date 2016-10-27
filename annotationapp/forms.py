from django import forms
from django.core.exceptions import ValidationError

import zipfile


class UploadForm(forms.Form):
    def clean_zip_file(self):
        zip_file = self.cleaned_data['zip_file']
        if not zipfile.is_zipfile(zip_file):
            raise ValidationError("The file type is not correct")

    zip_file = forms.FileField(
        label='Select a file',
        help_text='Zip file with the sounds'
    )
