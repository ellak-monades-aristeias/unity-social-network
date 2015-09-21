# -*- coding: utf-8 -*-
import uuid

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, Textarea, TextInput, DateInput,RadioSelect,CheckboxInput
from userprofiles.models import UserProfile, Activities
from registration.models import RegistrationProfile
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from cicu.widgets import CicuUploaderInput
from django.conf import settings
from userprofiles.settings import up_settings


class MyForm (ModelForm):
	class Meta:
		model = UserProfile
		fields = ['role']
		
		
class UserProfileForm (ModelForm):
	class Meta:
		model = User
		fields = [ 'username', 'email' ,'password']


class UserEditProfileForm (ModelForm):
	def __init__(self, *args, **kwargs):
		super(UserEditProfileForm, self).__init__(*args, **kwargs)
		SEX_CHOICES = (
			('Male', 'Male'),
			('Female', 'Female'),
		)
		
		STUDIES_CHOICES = (
			('Basic studies', 'Basic studies'),
			('Bachelor degree', 'Bachelor degree'),
			('Master degree', 'Master degree'),
			('PhD degree', 'PhD degree'),
		)		

		STATUS_CHOICES = (
			('Single', 'Single'),
			('Married', 'Married'),
			('Divorced', 'Divorced'),
		)
		self.fields['gender'] = forms.ChoiceField(widget=forms.RadioSelect(),choices=SEX_CHOICES, label="Gender")
		self.fields['status'] = forms.ChoiceField(widget=forms.RadioSelect(),choices=STATUS_CHOICES, label="Family Status")
		self.fields['studies'] = forms.ChoiceField(widget=forms.RadioSelect(),choices=STUDIES_CHOICES, label="Studies")
		self.fields['activities'] = forms.ModelMultipleChoiceField(queryset=Activities.objects.all(), required=False, widget=forms.CheckboxSelectMultiple, label="Activities")
		

	class Meta:	
		model = UserProfile
		
		cicuOptions = {
		    'ratioWidth': '', #if image need to have fix-width ratio
		    'ratioHeight':'', #if image need to have fix-height ratio
		    'sizeWarning': 'False', #if True the crop selection have to respect minimal ratio size defined above.
		}
		fields = [ 'thumbnailURL','aboutMe','location', 'birthday','displayName', 'name', 'status','studies', 'activities',  'favouriteFood', 'favouriteSport', 'gender', 'interests' ]
		widgets = {
            		'aboutMe': Textarea(attrs={'class':'form-control', 'row':'5','placeholder':'Say something for you!'}),
			'displayName': TextInput(attrs={'class':'form-control'}),
			'birthday': DateInput(attrs={'class':'datepicker form-control', 'placeholder':'dd/mm/yyyy'}),
			'name': TextInput(attrs={'class':'form-control'}),
			'status': Textarea(attrs={'class':'form-control'}),
			'location': TextInput(attrs={'class':'form-control', 'placeholder':'πχ. Athens'}),
			'studies': TextInput(attrs={'class':'form-control'}),
			'activities': TextInput(attrs={'class':'form-control'}),
			'favouriteFood': Textarea(attrs={'class':'form-control'}),
			'favouriteSport': Textarea(attrs={'class':'form-control'}),
			'interests': Textarea(attrs={'class':'form-control'}),
			'gender': TextInput(attrs={'class':'form-control'}),
			'thumbnailURL': TextInput(attrs={'id':'thumbURL','class':'form-control',}),
        	}


		
userProfileFormset = inlineformset_factory(User, UserProfile, fields=('role',), can_delete=False)


class RegistrationForm(forms.Form):
    username = forms.RegexField(label=_("Username"), max_length=30,regex=r'^[\w.-]+$', error_messages={'invalid': _('This value may contain only letters, numbers and ./-/_ characters.')})

    email = forms.EmailField(label=_('E-mail'))
    email_repeat = forms.EmailField(label=_('E-mail (repeat)'), required=True)

    password = forms.CharField(label=_('Password'),widget=forms.PasswordInput(render_value=False))
    password_repeat = forms.CharField(label=_('Password (repeat)'),widget=forms.PasswordInput(render_value=False))

    first_name = forms.CharField(label=_('First name'), required=False)
    last_name = forms.CharField(label=_('Last name'), required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        if not up_settings.DOUBLE_CHECK_EMAIL:
            del self.fields['email_repeat']

        if not up_settings.DOUBLE_CHECK_PASSWORD:
            del self.fields['password_repeat']

        if not up_settings.REGISTRATION_FULLNAME:
            del self.fields['first_name']
            del self.fields['last_name']

        if up_settings.EMAIL_ONLY:
            self.fields['username'].widget = forms.widgets.HiddenInput()
            self.fields['username'].required = False

    def _generate_username(self):
        """ Generate a unique username """
        while True:
            # Generate a UUID username, removing dashes and the last 2 chars
            # to make it fit into the 30 char User.username field. Gracefully
            # handle any unlikely, but possible duplicate usernames.
            username = str(uuid.uuid4())
            username = username.replace('-', '')
            username = username[:-2]

            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                return username

    def clean_username(self):
        if up_settings.EMAIL_ONLY:
            username = self._generate_username()
        else:
            username = self.cleaned_data['username']
            if User.objects.filter(username__iexact=username):
                raise forms.ValidationError(
                    _(u'A user with that username already exists.'))

        return username

    def clean_email(self):
        if not up_settings.CHECK_UNIQUE_EMAIL:
            return self.cleaned_data['email']

        new_email = self.cleaned_data['email']

        emails = User.objects.filter(email__iexact=new_email).count()

        if up_settings.USE_EMAIL_VERIFICATION:
            from userprofiles.contrib.emailverification.models import EmailVerification

            emails += EmailVerification.objects.filter(
                new_email__iexact=new_email, is_expired=False).count()

        if emails > 0:
            raise forms.ValidationError(
                _(u'This email address is already in use. Please supply a different email address.'))

        return new_email

    def clean(self):
        if up_settings.DOUBLE_CHECK_EMAIL:
            if 'email' in self.cleaned_data and 'email_repeat' in self.cleaned_data:
                if self.cleaned_data['email'] != self.cleaned_data['email_repeat']:
                    raise forms.ValidationError(_('The two email addresses do not match.'))

        if up_settings.DOUBLE_CHECK_PASSWORD:
            if 'password' in self.cleaned_data and 'password_repeat' in self.cleaned_data:
                if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                    raise forms.ValidationError(_('You must type the same password each time.'))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        if up_settings.USE_ACCOUNT_VERIFICATION:
            from userprofiles.contrib.accountverification.models import AccountVerification

            new_user = AccountVerification.objects.create_inactive_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
            )
        else:
            new_user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email']
            )

        if up_settings.REGISTRATION_FULLNAME:
            new_user.first_name = self.cleaned_data['first_name']
            new_user.last_name = self.cleaned_data['last_name']

            new_user.save()

        if hasattr(self, 'save_profile'):
            self.save_profile(new_user, *args, **kwargs)

        return new_user
        
'''       
        
class MyRegistrationForm (ModelForm):
	class Meta:
		model = UserProfile
		fields =  ['user' ,'role','aboutMe']
'''
