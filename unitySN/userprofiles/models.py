    # -*- coding: utf-8 -*-

#TODO Install new Crop Image app as https://django-image-cropping.readthedocs.org/en/latest/

from django.db import models
from django.contrib.auth.models import User
from registration.models import RegistrationProfile
from django.utils.translation import ugettext_lazy as _
#from cicu.widgets import CicuUploaderInput
from django.conf import settings
from django import forms
from django_cas_ng.signals import cas_user_authenticated
from django.dispatch import receiver
from notifications import notify
from roles.models import Role


try:
    from django.contrib.auth.models import SiteProfileNotAvailable
except ImportError: # django >= 1.7
    SiteProfileNotAvailable = type('SiteProfileNotAvailable', (Exception,), {})


class uploadedImage (models.Model):
    image = models.ImageField(verbose_name="", null=True, blank=True, upload_to=settings.MEDIA_ROOT, max_length=300)

# class freeCrop(forms.ModelForm):
#     class Meta:
#         model = uploadedImage
#         cicuOptions = {
#             'ratioWidth': '', #if image need to have fix-width ratio
#             'ratioHeight':'', #if image need to have fix-height ratio
#             'sizeWarning': 'False', #if True the crop selection have to respect minimal ratio size defined above.
#         }
#         widgets = {
#             'image': CicuUploaderInput(options=cicuOptions)
#         }
#         exclude=[]
#
#
# class profileCrop(forms.ModelForm):
#
#     class Meta:
#         model = uploadedImage
#         cicuOptions = {
#             'ratioWidth': '200', #if image need to have fix-width ratio
#             'ratioHeight':'200', #if image need to have fix-height ratio
#             'sizeWarning': 'False', #if True the crop selection have to respect minimal ratio size defined above.
#         }
#         widgets = {
#             'image': CicuUploaderInput(options=cicuOptions)
#         }
#         exclude=[]

class Activities(models.Model):
    activity = models.CharField(max_length=200L)

    def __str__(self):
        return str(self.activity)

    def __unicode__(self):
        return unicode(self.activity)

    class Meta:
        verbose_name = _("Activities")
        verbose_name_plural= _("Activities")


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.ForeignKey(Role)
    displayName = models.CharField(verbose_name="Display Name",max_length=45L, blank=True)
    email = models.CharField(verbose_name="E-mail",max_length=45L, blank=True)
    name = models.CharField(verbose_name="Name",max_length=45L, blank=True)
    image = models.ImageField(upload_to='user_images', verbose_name=_('Avatar'), blank=True, null=True)
    thumbnailURL = models.CharField(verbose_name="Image",max_length=200L, db_column='thumbnailURL', blank=True,
                                    default='/static/main/img/user.png')
    gender = models.CharField(verbose_name="Gender",max_length=45L, blank=True)
    aboutMe = models.TextField(verbose_name="Description",blank=True)
    location = models.CharField(verbose_name="Location",max_length=45L, blank=True)
    status = models.CharField(verbose_name="Family Status",max_length=45L, blank=True)

    activities = models.ManyToManyField(Activities,blank=True)
    studies = models.TextField(verbose_name="Studies",blank=True)
    birthday = models.DateField(verbose_name="Birthday",null=True, blank=True)
    favouriteFood = models.TextField(verbose_name="favourite Food",blank=True)
    favouriteSport = models.TextField(verbose_name="favourite Sport ",blank=True)

    interests = models.CharField(verbose_name="Interests",max_length=45L, blank=True)

#     class Meta:
#         abstract = True
#
# class StudentProfile(UserProfile):
#     aboutMe = models.TextField(verbose_name="Description",blank=True)
#     location = models.CharField(verbose_name="Location",max_length=45L, blank=True)
#     status = models.CharField(verbose_name="Family Status",max_length=45L, blank=True)
#
# class BusinessProfile(UserProfile):
#
#     #ADDED FOR WALL POSTS
#     #image = models.ImageField(upload_to='user_images', verbose_name=_('Avatar'), blank=True, null=True)
#     #friends = models.ManyToManyField(User, verbose_name=_('Friends'), blank=True, null=True, related_name='friends')
#     #last_visit = models.DateTimeField(blank=True, auto_now=True, verbose_name=_('Last visit'))
#
#     aboutMe = models.TextField(verbose_name="Description",blank=True)
#     location = models.CharField(verbose_name="Location",max_length=45L, blank=True)
#     status = models.CharField(verbose_name="Family Status",max_length=45L, blank=True)
#
#     activities = models.ManyToManyField(Activities,blank=True)
#     studies = models.TextField(verbose_name="Studies",blank=True)
#     birthday = models.DateField(verbose_name="Birthday",null=True, blank=True)
#     favouriteFood = models.TextField(verbose_name="favourite Food",blank=True)
#     favouriteSport = models.TextField(verbose_name="favourite Sport ",blank=True)
#
#     interests = models.CharField(verbose_name="Interests",max_length=45L, blank=True)
#     #company = models.CharField(max_length=50, blank=True)

    @receiver(cas_user_authenticated)
    def cas_populate_user_receiver(sender, user, attributes, ticket, service, **kwargs):
        print "Signal received"
        notify.send(user, recipient=user, verb='Your account has been populated from CAS')
        print ticket
        print service
        print attributes
        print repr(attributes).decode("unicode-escape")
        print type(attributes)
        print attributes.get('sn')
        print "username "
        print user.username
        user.last_name = attributes.get('sn')
        user.save()
        role1 = Role.objects.get(type__iexact= "user")
        print role1
        UserProfile.objects.get_or_create(user=user, role= role1, displayName=attributes.get('givenName'), email=attributes.get('mail'))
        print "Profile created"

    def __unicode__(self):
        return self.user.username


    def __str__(self):
        return str(self.user)
    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')




User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])	
