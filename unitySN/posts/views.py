from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from userprofiles.models import UserProfile
from notifications import notify

from .import  models, compat
from .forms import Post_Form
import re

import urlparse
import httplib
import opengraph
User = compat.get_user_model()


@login_required()
def new_post (request):
    image_url = ""
    viewer = request.user
    owner_user = request.user
    owner_user_role = UserProfile.objects.get( user_id = request.user.id )
    if request.method == 'POST':
        # TODO Handle Upload Image on new post
        # form = freeCrop(request.POST) # A form bound to the POST data
        # if form.is_valid(): # All validation rules pass
        #         new_event = form.save()
        #         #return HttpResponseRedirect('/user/profile/'+request.user.username)
        #         #return HttpResponseRedirect('/file-upload/cicu-freecrop/?id='+str(new_event.id))
        #     a = new_event.id
        #
        #     # if uploadedImage.objects.get(id=a).image:
        #     #     image_url = "###uploaded_image###"+uploadedImage.objects.get(id=a).image.url+"##!uploaded_image!##"
        form = Post_Form(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            if content != "" or image_url!="":
                content = content + image_url
                actor_name = form.cleaned_data['actor_name']
                post_target = form.cleaned_data['target']
                print post_target
                #####################
                owner_user = User.objects.get(username__exact = actor_name) # user creation
                owner_user_role = UserProfile.objects.get( user_id = owner_user.id )
                #relationships =  [relationship for relationship in RelationshipStatus.objects.all().filter (to_role_id = user_role.role_id)]

                content = rendered_content (content,request)
                print content

                # if post_target == "Private":
                #     print "Private target"
                #     action.send(viewer, verb='posted', action_object = owner_user, target= viewer,  post_content=content) # action creation
                # elif post_target == "Public":
                #     print "public target"
                #     print owner_user_role.role_id
                #     if  (RelationshipStatus.objects.all().filter (to_role_id = owner_user_role.role_id).count() == 0 ):
                #         print " No relationship found "
                #         if  (RelationshipStatus.objects.all().filter (to_role_id__isnull=True ).count() >= 0 ):
                #             for relationship in RelationshipStatus.objects.all().filter (to_role_id__isnull=True):
                #                 action.send(viewer, verb='posted', action_object = owner_user, target=relationship,  post_content=content)
                #     else:
                #         for relationship in RelationshipStatus.objects.all().filter (to_role_id = owner_user_role.role_id):
                #             action.send(viewer, verb='posted', action_object = owner_user, target=relationship,  post_content=content) # action creation
                #         if  (RelationshipStatus.objects.all().filter (to_role_id__isnull=True ).count() >= 0 ):
                #             for relationship in RelationshipStatus.objects.all().filter (to_role_id__isnull=True):
                #                 action.send(viewer, verb='posted', action_object = owner_user, target=relationship,  post_content=content)
                # else:
                #     for relationship in RelationshipStatus.objects.all().filter (Q(to_role_id = owner_user_role.role_id) & Q(name = post_target )):
                #         action.send(viewer, verb='posted', action_object = owner_user, target=relationship,  post_content=content) # action creation
                #
                # # notification NOT USED
                # '''
                # if request.user.id != user.id:
                #     print user.id
                #     notify.send(request.user,  recipient=user, verb='wall_post' )
                # '''
        else:
            print "ERROR IN VALIDATION"
            print form.errors
    else:
        form = Post_Form()

    return render(request, 'posts/new.html', {'form': form})



def rendered_content( content,request ):
#for wall_post in wall_posts:
	title = ''
	desc = ''
	site_image = ''
	article_title = ''
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
	mentions = re.findall('\@\w+', content)
	r = re.compile('###uploaded_image###(.*?)##!uploaded_image!##')
	m = r.search(content)
	if m:
		content = content.replace(m.group(1), "").replace("###uploaded_image###", "").replace("##!uploaded_image!##", "") +"<br/><div class='row'><div class='col-sm-6 col-md-3'><a href='"+m.group(1)+"' target='_blank' class='thumbnail'><img data-src='holder.js/300' src='"+m.group(1)+"'/></a></div></div>"

	for mention in mentions:
		mentioned_username= mention.replace('@','')
		mentioned_user = User.objects.get(username=mentioned_username)
		if mentioned_user:
			notify.send(request.user, recipient=mentioned_user, verb='post_mention' )
			content=content.replace(mention, '<a href="/user/profile/'+mentioned_username+'">'+mention+'</a>')
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
			content = content+"<br/><div class='row'><div class='col-sm-6 col-md-3'><a href='"+url+"' target='_blank' class='thumbnail'><img data-src='holder.js/300' src='"+url+"'/></a></div></div>"
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
								content = content.replace(url,"<a href='"+url+"' target='_blank'>"+url+"</a>")+"<br/><br/><iframe width='300' height='200' src='//www.youtube.com/embed/"+video+"' frameborder='0' allowfullscreen></iframe>"
							elif k == 'site_name' and l == 'Vimeo':
								url_data = urlparse.urlparse(url)
								video = url_data.path
								content = content.replace(url,"<a href='"+url+"' target='_blank'>"+url+"</a>")+"<br/><br/><iframe src='//player.vimeo.com/video"+video+"' width='300' height='200' frameborder='0' webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe> <p></p>"
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
						content = content +"<br/><table><tr><td><img width='50' src='"+site_image+"'</td><td><a href='"+url+"' target='_blank'/>"+article_title+"</a><br/>"+title+"</td></td></table>"
					elif x=='type':
						for k,l in og.items():
							if k == 'site_name':
								title = l
							elif k=='description':
								desc = l
							elif k=='image':
								site_image = l
						content = content.replace(url, "<table><tr><td><img width='50' src='"+site_image+"'</td><td><a href='"+url+"' target='_blank'/>"+title+"</a><br/>"+desc+"</td></td></table>")
			else:
				content = content.replace(url, "<a href='"+url+"' target='_blank'>"+url+"</a>")

	return content