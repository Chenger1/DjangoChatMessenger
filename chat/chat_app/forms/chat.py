from django import forms

from _db.models import Group


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )
