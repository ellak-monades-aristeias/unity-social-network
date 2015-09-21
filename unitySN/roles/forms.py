from django.forms import ModelForm
from .models import Role
from django.forms.models import modelformset_factory
from djangoformsetjs.utils import formset_media_js


class RoleForm(ModelForm):
    class Meta:
         model = Role
         fields = ['type', 'desc',]

