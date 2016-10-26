from django import forms


class UploadForm(forms.Form):
    zip_file = forms.FileField(
        label='Select a file',
        help_text='xip file with the sounds'
    )
