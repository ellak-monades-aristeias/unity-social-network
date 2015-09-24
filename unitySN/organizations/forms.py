from django import forms
from django.contrib.sites.models import get_current_site
from django.utils.translation import ugettext_lazy as _

from organizations.models import Organization, OrganizationUser, get_user_model
from organizations.utils import create_organization
from organizations.backends import invitation_backend
from cicu.widgets import CicuUploaderInput
from django.forms import TextInput,Textarea


class OrganizationForm(forms.ModelForm):
    """Form class for updating Organizations"""

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(OrganizationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        fields = ['name','description', 'image']

	cicuOptions = {
            'ratioWidth': '200',      #fix-width ratio, default 0
            'ratioHeight':'200',      #fix-height ratio , default 0
            'sizeWarning': 'True',    #if True the crop selection have to respect minimal ratio size defined above. Default 'False'
	}
	widgets = {
	    'description': Textarea(attrs={'class':'form-control'}),
	    'name': TextInput(attrs={'class':'form-control'}),
	    'image': CicuUploaderInput(options=cicuOptions)
	}


    def save(self, *args, **kwargs):
	image = self.request.POST.get('image_field')
	commit = kwargs.pop('commit', True)
        instance = super(OrganizationForm, self).save(*args, commit = False, **kwargs)
        instance.image = image
        if commit:
            instance.save()
        return instance



class OrganizationUserForm(forms.ModelForm):
    """Form class for updating OrganizationUsers"""

    class Meta:
        model = OrganizationUser
        exclude = ('organization', 'user')

    def clean_is_admin(self):
        is_admin = self.cleaned_data['is_admin']
        if self.instance.organization.owner.organization_user == self.instance and not is_admin:
            raise forms.ValidationError(_("The organization owner must be an admin"))
        return is_admin


class OrganizationUserAddForm(forms.ModelForm):
    """Form class for adding OrganizationUsers to an existing Organization"""
    email = forms.EmailField(max_length=75)

    def __init__(self, request, organization, *args, **kwargs):
        self.request = request
        self.organization = organization
        super(OrganizationUserAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = OrganizationUser
        exclude = ('user', 'organization')

    def save(self, *args, **kwargs):
        """
        The save method should create a new OrganizationUser linking the User
        matching the provided email address. If not matching User is found it
        should kick off the registration process. It needs to create a User in
        order to link it to the Organization.
        """
        try:
            user = get_user_model().objects.get(email__iexact=self.cleaned_data['email'])
        except get_user_model().MultipleObjectsReturned:
            raise forms.ValidationError(_("This email address has been used multiple times."))
        except get_user_model().DoesNotExist:
            user = invitation_backend().invite_by_email(
                    self.cleaned_data['email'],
                    **{'domain': get_current_site(self.request),
                        'organization': self.organization})
        return OrganizationUser.objects.create(user=user,
                organization=self.organization,
                is_admin=self.cleaned_data['is_admin'])

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.organization.users.filter(email=email):
            raise forms.ValidationError(_("There is already an organization member with this email address!"))
        return email


class OrganizationAddForm(forms.ModelForm):
    """
    Form class for creating a new organization, complete with new owner, including a
    User instance, OrganizationUser instance, and OrganizationOwner instance.
    """
    '''
    email = forms.EmailField(max_length=75,
            help_text=_("The email address for the account owner"))
	'''
	
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(OrganizationAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        fields = ['name','description','image']
        exclude = ('users', 'is_active')
	
	cicuOptions = {
            'ratioWidth': '200',      #fix-width ratio, default 0
            'ratioHeight':'200',      #fix-height ratio , default 0
            'sizeWarning': 'True',    #if True the crop selection have to respect minimal ratio size defined above. Default 'False'
	}
	widgets = {
	    'name': TextInput(attrs={'class':'form-control'}),
	    'description': Textarea(attrs={'class':'form-control'}),
	    'image': CicuUploaderInput(options=cicuOptions)
	}

    def save(self, **kwargs):
	image = self.request.POST.get('image_field')
        is_active = True
        user = self.request.user
        return create_organization(user, self.cleaned_data['name'], self.cleaned_data['description'], image, is_active=is_active)


class SignUpForm(forms.Form):
    """
    From class for signing up a new user and new account.
    """
    name = forms.CharField(max_length=50,
            help_text=_("The name of the organization"))
    slug = forms.SlugField(max_length=50,
            help_text=_("The name in all lowercase, suitable for URL identification"))
    email = forms.EmailField()
