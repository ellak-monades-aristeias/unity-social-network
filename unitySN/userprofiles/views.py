# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import json as simplejson
from userprofiles.settings import up_settings
from userprofiles.utils import get_form_class
from userprofiles.forms import MyForm
from userprofiles.forms import RegistrationForm
from userprofiles.forms import UserEditProfileForm
from django.forms.formsets import formset_factory
from userprofiles.models import freeCrop,profileCrop
from userprofiles.models import UserProfile
from registration.models import RegistrationProfile
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from userprofiles.forms import UserProfileForm, userProfileFormset
from registration.models import RegistrationProfile
from registration.forms import RegistrationForm
from registration.users import UserModel
from django.contrib.sites.models import Site
from registration import signals
from django.template import RequestContext
from django.contrib.auth.models import User
#from actstream_old.models import Action
from userprofiles.models import UserProfile
from relationships.models import RelationshipStatus, Relationship
from django.utils.encoding import smart_unicode
from itertools import chain
from django.core import serializers
from django.utils.encoding import force_text
from django.conf import settings
import json
from urlparse import urlparse
import opengraph
import urllib
import urlparse 
import httplib
import ast
import random
from random import shuffle
from django.contrib.contenttypes.models import ContentType
from notifications import notify

def get_all_users(request):
	user_list = User.objects.all()
	#ctx = {'user_list':user_list}
	return render(request, "users.html", {	'user_list':user_list })

def add_user(request):
    form = UserProfileForm()
    user_formset = userProfileFormset(instance=RegistrationProfile())
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
			#user_profile = form.save()
			data = form.cleaned_data
			site = Site.objects.get_current()
			new_user_instance = UserModel().objects.create_user(**form.cleaned_data)
			new_user = RegistrationProfile.objects.create_inactive_user(
				new_user=new_user_instance,
				site=site,
				send_email=False,
				request=request,
				)
			#new_user = RegistrationProfile.objects.create_inactive_user(data['username'] , data['email'],data['password'], site)
			#signals.user_registered.send(sender=self.__class__, user=new_user,request=request)
			user_formset = userProfileFormset(request.POST, request.FILES, instance=new_user_instance)

			if user_formset.is_valid():
				user_formset.save()
				return render(request, "userprofiles/registration_complete.html", {	
				})
    
    return render(request, "userprofiles/registration.html", {
        'form': form, 
        'user_formset': user_formset,
        'action' : 'Create'
    })


def add_developer(request):
    form = UserProfileForm()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
			#user_profile = form.save()
			data = form.cleaned_data
			site = Site.objects.get_current()
			new_user = RegistrationProfile.objects.create_inactive_user(data['username'] , data['email'],data['password'], site , send_email = False)
			userprofileobj = UserProfile(user = new_user, role_id=11, displayName = data['username'], thumbnailURL= '/static/main/img/user.png ')
			userprofileobj.save()

			s_admins = User.objects.filter(is_superuser = 1)
			for s_admin in s_admins:
				notify.send(new_user, recipient=s_admin, verb='signed_up' )

			return HttpResponseRedirect('/')
    


    return render(request, "userprofiles/registration.html", {
        'form': form, 
        'action' : 'Create'
    })

def autocomplete_user(request):
    term = request.GET.get('term') #jquery-ui.autocomplete parameter
    profiles = UserProfile.objects.filter(displayName__icontains=term) #lookup for a city
    
    res = []
    for p in profiles:
	 user = User.objects.get(id=p.user.id)
	 #make dict with the metadatas that jquery-ui.autocomple needs (the documentation is your friend)
	 dict = {'id':p.displayName, 'label':p.displayName, 'value':user.username, 'image': p.thumbnailURL}
	 res.append(dict)
    return HttpResponse(simplejson.dumps(res))

def user_search(request):
	suggested_users = []
	random_users = []
	contacts = []

	if str(request.user.profile.role) == "Developer":
		users = UserProfile.objects.all()
		for user in users:
			if str(user.role) == "Developer": #finding developers
				print "is Developer"
				if request.user != User.objects.get(id = user.user_id): # remove the request user
					random_users.append(User.objects.get(id = user.user_id)) # add users to list
	else:
		users = User.objects.all()
		user_relationships = RelationshipStatus.objects.all().filter( to_role_id = request.user.profile.role.id )
		for status in user_relationships:
			contacts.extend(request.user.relationships.get_related_to(status=status))
		users = list(set(users)^set(contacts))
		for user in users:
			if not user.is_superuser and user != request.user and str(UserProfile.objects.get(user_id = user.id).role) != "Developer": # user MUST NOT be superuser,same user and developer
				random_users.append(user)
				common_activities = list(set(user.profile.activities.all()).intersection(request.user.profile.activities.all()))
				if len(common_activities) >= 3:
					suggested_users.append(user)
				else:
					if len(common_activities) == 2:
						if user.profile.studies == request.user.profile.studies:					
							suggested_users.append(user)
						else:
							if user.profile.status == request.user.profile.status:
								suggested_users.append(user)
					else:
						if len(common_activities) == 1:
							if user.profile.status == request.user.profile.status or user.profile.studies == request.user.profile.studies:
								suggested_users.append(user)

		random.shuffle(random_users)
		del random_users[20:]
				
					
	return render(request, "userprofiles/search.html", {'users':suggested_users,'random_users':random_users} )
	

def profile_view(request, username):
	SEX_CHOICES = (
		('male', 'Male'),
		('female', 'Female'),
	)
	ACTIVITY_CHOICES = (
		('art', 'Art'),
		('cooking', 'cooking'),
		('family', 'family'),
		('reading', 'Διάβασμα'),
		('trips', 'Ταξίδια'),
		('gym', 'Γυμναστήριο'),
		('walking', 'Περπάτημα'),
		('nature', 'Φύση'),
		('technology', 'Τεχνολογία'),
		('science', 'Επιστήμη'),
		('photography', 'Φωτογραφία'),
		('pets', 'Κατοικίδια'),
		('music', 'Μουσική'),
		('cinema', 'Κινηματογράφος'),
		('theater', 'Θέατρο'),
		('gardening', 'Κηπουρική'),
		('painting', 'Ζωγραφική'),
	)
	STATUS_CHOICES = (
		('single', 'Άγαμος'),
		('married', 'Έγγαμος'),
		('divorced-widowed', 'Διαζευγμένος-Χήρος'),
	)
	owner_user = User.objects.get(username__exact = username)
	owner_user_role = UserProfile.objects.get( user_id = owner_user.id )
	profile = owner_user.profile
	#wall_posts = get_actions_by_user( request.user , owner_user)
	user_relationships = []
	activities = []
	contacts = []
	if owner_user == request.user :
			user_relationships = RelationshipStatus.objects.all().filter( to_role_id = owner_user_role.role_id )
			for status in user_relationships:
				contacts.extend(request.user.relationships.get_related_to(status=status))
			
	form = freeCrop() # A form bound to the POST data

	
 
	context = {				  'otheruser':owner_user,
					  'username': owner_user.username,      
					  'displayName':profile.displayName,
					  'name':profile.name,
					  'aboutMe':profile.aboutMe,
					  'status':profile.status,
					  'location':profile.location,
					  'studies': profile.studies,
					  'activities':profile.activities.all,
					  'birthday':profile.birthday,
					  'favouriteFood':profile.favouriteFood,
					  'favouriteSport':profile.favouriteSport,
					  'gender':profile.gender,
					  'interests':profile.interests,
					  'role':profile.role,
					  #'wall_posts' : wall_posts ,
					  'image_form': form,
					  'thumbnailURL': profile.thumbnailURL,
					  'MEDIA_URL': settings.MEDIA_URL,
					  'user_relationships' : user_relationships,
					  'contacts': contacts,}
	return render(request, 'userprofiles/profile.html', context)
'''
def rendered_wall_posts( wall_posts ):
	for wall_post in wall_posts:
		title = ''
		desc = ''
		site_image = ''
		article_title = ''
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', wall_post.data['post_content'])
		for url in urls: 
			parse_obj = urlparse.urlparse(url)
			site = parse_obj.netloc
			path = parse_obj.path
			conn = httplib.HTTPConnection(site)
			conn.request('HEAD',path)
			response = conn.getresponse()
			conn.close()
			ctype = response.getheader('Content-Type')
			if response.status < 400 and ctype.startswith('image'):
				wall_post.data['post_content'] = wall_post.data['post_content']+"<br/><a href='"+url+"' target='_blank'><img width=300 src='"+url+"' target = '_blank'/></a>"
			else:
				og = opengraph.OpenGraph(url)
				if not len(og.items()) == 2:
					for x,y in og.items():
						if x == 'type' and y == 'video':
							for k,l in og.items():
								if k == 'site_name' and l == 'YouTube':
							
									url_data = urlparse.urlparse(url)
									query = urlparse.parse_qs(url_data.query)
									video = query["v"][0]
									wall_post.data['post_content'] = wall_post.data['post_content'].replace(url,"")+"<br/><iframe width='300' height='200' src='//www.youtube.com/embed/"+video+"' frameborder='0' allowfullscreen></iframe>"
								elif k == 'site_name' and l == 'Vimeo':
									url_data = urlparse.urlparse(url)
									video = url_data.path
									wall_post.data['post_content'] = wall_post.data['post_content'].replace(url,"")+"<br/><iframe src='//player.vimeo.com/video"+video+"' width='300' height='200' frameborder='0' webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe> <p></p>"
						elif x == 'type' and y == 'article':
							for k,l in og.items():
								if k == 'title':
									article_title = l
								elif k == 'site_name':
									title = l
								elif k=='description':
									desc = l
								elif k=='image':
									site_image = l
							wall_post.data['post_content'] = wall_post.data['post_content'] +"<br/><table><tr><td><img width='50' src='"+site_image+"'</td><td><a href='"+url+"' target='_blank'/>"+article_title+"</a><br/>"+title+"</td></td></table>"
						elif x=='type':
							for k,l in og.items():
								if k == 'site_name':
									title = l
								elif k=='description':
									desc = l
								elif k=='image':
									site_image = l
							wall_post.data['post_content'] = wall_post.data['post_content'].replace(url, "<table><tr><td><img width='50' src='"+site_image+"'</td><td><a href='"+url+"' target='_blank'/>"+title+"</a><br/>"+desc+"</td></td></table>")
				else:
					wall_post.data['post_content'] = wall_post.data['post_content'].replace(url, "<a href='"+url+"' target='_blank'>"+url+"</a>")	
	return wall_posts	


#---------This code should be in acstream.views----
def get_actions_by_user( viewer, owner ):
	wall_posts = []
	wall_posts_null_relationships = []
	wall_posts_ids = []
		# Viewer is owner
	if viewer == owner:
		wall_posts_distinct = list (Action.objects.filter( Q (action_object_object_id = owner.id ) & Q(verb='posted')).values_list('timestamp').distinct())# all distinct wall posts
		for y in Action.objects.filter(verb='posted'):
			for x in wall_posts_distinct:
				if y.timestamp ==x[0]:
					wall_posts_distinct.remove(x)
					wall_posts_ids.append(y.id)
				
		for wp_id in wall_posts_ids:
			wall_posts.extend(Action.objects.filter( id = wp_id ) )

	else:
		# Collect users role
		print viewer
		print owner
		owner_user_role = UserProfile.objects.get( user_id = owner.id )
		viewer_user_role = UserProfile.objects.get( user_id = viewer.id )
		
		for relationship_status in RelationshipStatus.objects.all().filter( Q(Q(to_role_id = owner_user_role.role_id) & Q(from_role_id = viewer_user_role.role_id) ) | Q( Q(to_role_id__isnull=True) & Q(from_role_id__isnull=True))):
			if relationship_status:
				print relationship_status.id
				if Relationship.objects.all().filter( Q(to_user_id = owner.id) & Q(from_user_id = viewer.id) & Q(status_id = relationship_status.id) ).exists():
					wall_posts = Action.objects.filter( Q(verb='posted' ) & Q(target_object_id = relationship_status.id) & Q(action_object_object_id = owner.id))
					#wall_posts = Action.objects.filter(target_object_id = relationship_status.id)
					#wall_posts = Action.objects.filter(action_object_object_id = owner.id)					
					
					print "RELATIONSHIP EXIST"
				else:
					print "NO RELATIONSHIP"
			else:
				print " NO RELATIONSHIP"

				
	return wall_posts
'''


class ProfileUpdateView(UpdateView):
    form_class = UserEditProfileForm
    
    model = UserProfile
    template_name = 'userprofiles/profile_change.html'

    def get(self, request, **kwargs):
	image_form = profileCrop()
        self.object = UserProfile.objects.get(user_id= request.user.id)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object=self.object, form=form)
	context['image_form']=image_form
	context['MEDIA_URL']=settings.MEDIA_URL
        return self.render_to_response(context, )


    def get_object(self, queryset=None):
		obj = UserProfile.objects.get(user_id=self.request.user.id)
		return obj


def profile_edit(request, username):
    owner_user = User.objects.get(username__exact = username)
    profile = owner_user.profile
    

    image_form = freeCrop(request.POST) # A form bound to the POST data
    

    eform = UserEditProfileForm( initial={'displayName':profile.displayName,
                      'name':profile.name,
                      'aboutMe':profile.aboutMe,
                      'status':profile.status,
                      'location':profile.location,
		      'studies':profile.studies,
                      'activities':profile.activities,
                      'birthday':profile.birthday,
                      'favouriteFood':profile.favouriteFood,
                      'favouriteSport':profile.favouriteSport,
                      'gender':profile.gender,
                      'interests':profile.interests,
                      'role':profile.role,
		      'thumbnail':profile.thumbnailURL,
                    },
                 instance = profile, 
                 data = request.POST)    

    if request.method == "POST":
        
        if eform.is_valid():
            profile = eform.save(commit = False)
            profile.save()
	if image_form.is_valid(): # All validation rules pass
		new_event = image_form.save()
		a = new_event.id
		#if uploadedImage.objects.get(id=a).image:
			#image_url = "###uploaded_image###"+uploadedImage.objects.get(id=a).image.url+"##!uploaded_image!##"
    return render_to_response('userprofiles/profile_change.html', {
        'form': eform, 
	'image_form': image_form,
	'MEDIA_URL': settings.MEDIA_URL,
    },context_instance=RequestContext(request))


def extented_view(request):
	RegistraionFromSet = formset_factory(RegistrationForm) 
	MyFromSet = formset_factory(MyForm)
	if request.method == "POST":
		 registraton_formset = RegistraionFromSet(request.POST, request.FILES, prefix='reg')
		 my_formset = MyFromSet(request.POST, request.FILES, prefix='my')
		 if registraton_formset.is_valid() and my_formset.is_valid():
			 print "DONE";
	else:
		registraton_formset = RegistraionFromSet(prefix='reg')
		my_formset = MyFromSet(prefix='my')
	
	return render_to_response('userprofiles/registration.html', {
        'registraton_formset': registraton_formset,
        'my_formset': my_formset,
    })
		
			

class RegistrationView(FormView):
    form_class = get_form_class(up_settings.REGISTRATION_FORM)
    template_name = 'userprofiles/registration.html'

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Automatically log this user in
        if up_settings.AUTO_LOGIN:
            if up_settings.EMAIL_ONLY:
                username = form.cleaned_data['email']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(self.request, user)

        return redirect(up_settings.REGISTRATION_REDIRECT)

registration = RegistrationView.as_view()


class RegistrationCompleteView(TemplateView):
    template_name = 'userprofiles/registration_complete.html'

    def get_context_data(self, **kwargs):
        return {
            'account_verification_active': up_settings.USE_ACCOUNT_VERIFICATION,
            'expiration_days': up_settings.ACCOUNT_VERIFICATION_DAYS,
        }

registration_complete = RegistrationCompleteView.as_view()
