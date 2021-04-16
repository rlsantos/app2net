from django import forms
from django.core.validators import FileExtensionValidator


class NADFileForm(forms.Form):
    nad_file = forms.FileField(validators=[FileExtensionValidator(['nad'])])
