from django import forms


class RebuildSiteForm(forms.Form):
    rebuild = forms.BooleanField(label="Force full rebuild")
