from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.generic import (ListView, DetailView, UpdateView, CreateView,
        DeleteView, FormView)
from userprofiles.models import freeCrop, UserProfile
from organizations.models import Organization, OrganizationUser
from organizations.mixins import (OrganizationMixin, OrganizationUserMixin,
        MembershipRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin)
from organizations.forms import (OrganizationForm, OrganizationUserForm,
        OrganizationUserAddForm, OrganizationAddForm, SignUpForm)
from organizations.utils import create_organization
from organizations.backends import invitation_backend, registration_backend
from collato1_8.actstream import Action
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from roleapp.models import Role


class BaseOrganizationList(ListView):
    queryset = Organization.active.all()
    context_object_name = "organizations"

    def get_queryset(self):
        return super(BaseOrganizationList, self).get_queryset().filter(users=self.request.user)
        

class BaseOrganizationDetail(OrganizationMixin, DetailView):
	def get_context_data(self, **kwargs):
		context = super(BaseOrganizationDetail, self).get_context_data(**kwargs)
		context['organization_users'] = self.organization.organization_users.all()
		context['organization'] = self.organization
		organization_ct = ContentType.objects.get(app_label="organizations", model="organization")
		if not self.organization.is_admin(self.request.user) and not self.request.user.is_superuser:
			context['admin'] = False
		else:
			context['admin'] = True	
		context['link'] = "/groups/"+str(self.organization.id)+"/delete/"+str(self.request.user.id)
		context['image_form'] = freeCrop(self.request.POST)
		context['wall_posts'] = Action.objects.filter( Q (target_object_id= self.organization.id) & Q(verb='posted') & Q(target_content_type_id = organization_ct.id ))
		return context


class BaseOrganizationCreate(CreateView):
    model = Organization
    form_class = OrganizationAddForm
    template_name = 'organizations/organization_form.html'
    
    def get_success_url(self):
        return reverse('all_groups')

    def get_form_kwargs(self):
        kwargs = super(BaseOrganizationCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class BaseOrganizationUpdate(OrganizationMixin, UpdateView):
    form_class = OrganizationForm
    template_name = 'organizations/organization_edit_form.html'

    def get_form_kwargs(self):
        kwargs = super(BaseOrganizationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class BaseOrganizationDelete(OrganizationMixin, DeleteView):
    def get_success_url(self):
        return reverse("organization_list")


class BaseOrganizationUserList(OrganizationMixin, ListView):
    def get(self, request, *args, **kwargs):
        self.organization = self.get_organization()
        self.object_list = self.organization.organization_users.all()
        context = self.get_context_data(object_list=self.object_list,
                organization_users=self.object_list,
                organization=self.organization)
        return self.render_to_response(context)


class BaseOrganizationUserDetail(OrganizationUserMixin, DetailView):
    pass


class BaseOrganizationUserCreate(OrganizationMixin, CreateView):
    form_class = OrganizationUserAddForm
    template_name = 'organizations/organizationuser_form.html'

    def get_success_url(self):
        return reverse('organization_user_list',
                kwargs={'organization_pk': self.object.organization.pk})

    def get_form_kwargs(self):
        kwargs = super(BaseOrganizationUserCreate, self).get_form_kwargs()
        kwargs.update({'organization': self.organization,
            'request': self.request})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.organization = self.get_object()
        return super(BaseOrganizationUserCreate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.organization = self.get_object()
        return super(BaseOrganizationUserCreate, self).post(request, *args, **kwargs)


class BaseOrganizationUserRemind(OrganizationUserMixin, DetailView):
    template_name = 'organizations/organizationuser_remind.html'
    # TODO move to invitations backend?

    def get_object(self, **kwargs):
        self.organization_user = super(BaseOrganizationUserRemind, self).get_object()
        if self.organization_user.user.is_active:
            raise Http404(_("Already active")) # TODO add better error
        return self.organization_user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        invitation_backend().send_reminder(self.object.user,
                **{'domain': get_current_site(self.request),
                    'organization': self.organization, 'sender': request.user})
        return redirect(self.object)


class BaseOrganizationUserUpdate(OrganizationUserMixin, UpdateView):
    form_class = OrganizationUserForm


class BaseOrganizationUserDelete(OrganizationUserMixin, DeleteView):
    def get_success_url(self):
        return reverse('organization_user_list',
                kwargs={'organization_pk': self.object.organization.pk})


class OrganizationSignup(FormView):
    """
    View that allows unregistered users to create an organization account.

    It simply processes the form and then calls the specified registration
    backend.
    """
    form_class = SignUpForm
    template_name = "organizations/signup_form.html"
    # TODO get success from backend, because some backends may do something
    # else, like require verification
    backend = registration_backend()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('organization_add')
        return super(OrganizationSignup, self).dispatch(request, *args,
                **kwargs)

    def get_success_url(self):
        if hasattr(self, 'success_url'):
            return self.success_url
        return reverse('organization_signup_success')

    def form_valid(self, form):
        """
        """
        user = self.backend.register_by_email(form.cleaned_data['email'])
        create_organization(user=user, name=form.cleaned_data['name'],
                slug=form.cleaned_data['slug'], is_active=False)
        return redirect(self.get_success_url())


def signup_success(self, request):
    return render(request, "organizations/signup_success.html", {})


class OrganizationList(BaseOrganizationList):
    pass


class OrganizationCreate(BaseOrganizationCreate):
    """
    Allows any user to create a new organization.
    """
    pass


class OrganizationDetail(MembershipRequiredMixin, BaseOrganizationDetail):
    pass


class OrganizationUpdate(AdminRequiredMixin, BaseOrganizationUpdate):
    pass


class OrganizationDelete(OwnerRequiredMixin, BaseOrganizationDelete):
    pass


class OrganizationUserList(MembershipRequiredMixin, BaseOrganizationUserList):
    pass


class OrganizationUserDetail(AdminRequiredMixin, BaseOrganizationUserDetail):
    pass


class OrganizationUserUpdate(AdminRequiredMixin, BaseOrganizationUserUpdate):
    pass


class OrganizationUserCreate(AdminRequiredMixin, BaseOrganizationUserCreate):
    pass


class OrganizationUserRemind(AdminRequiredMixin, BaseOrganizationUserRemind):
    pass


class OrganizationUserDelete(AdminRequiredMixin, BaseOrganizationUserDelete):
    pass

def all_groups(request):

    all_organizations = Organization.active.all()
    user_organizations = Organization.active.all().filter(users=request.user)

    #finding developers
    users_dev = []
    developer_role = Role.objects.all().filter(type = "Developer")
    developers = UserProfile.objects.all().filter( role = developer_role)

    for developer in developers:
        try:
            users_dev += User.objects.all().filter(id = developer.user_id)
        except User.DoesNotExist:
            print "User does not exist"

    all_developer_organizations =  Organization.active.all().filter(users__in = users_dev).distinct()
    all_user_organizations = Organization.objects.exclude(pk__in= all_developer_organizations )


    if str(request.user.profile.role) == "Developer":
        all_organizations = all_developer_organizations
    else:
        all_organizations = all_user_organizations

    user_organizations = Organization.active.all().filter(users=request.user)
    other_organizations =all_organizations.exclude(pk__in=user_organizations)
	#print all_organizations
    return render(request, "organizations/organization_list.html", {'all_organizations':all_organizations, 'user_organizations':user_organizations, 'other_organizations':other_organizations, })
	

def user_not_member(request,organization_pk):

	organization_ct = ContentType.objects.get(app_label="organizations", model="organization")
	wall_posts= Action.objects.filter( Q (target_object_id= organization_pk) & Q(verb='posted') & Q(target_content_type_id = organization_ct.id ))
	organization = Organization.objects.get(id = organization_pk )
	link = "/groups/"+str(organization_pk)+"/add/"+str(request.user.id)
	image_form = freeCrop(request.POST)
	
	return render(request, "organizations/organization_detail_visitor.html", {'wall_posts':wall_posts, 'organization':organization, 'link':link, 'image_form':image_form})
	
def add_user(request,organization_pk, user_pk):
	user = User.objects.get( id = user_pk)
	organization = Organization.objects.get(id = organization_pk )
	OrganizationUser.objects.create(user=user,organization=organization)
	return HttpResponseRedirect('/groups/'+organization_pk)
	
def delete_user(request,organization_pk, user_pk):	
	user = User.objects.get( id = user_pk)
	organization = Organization.objects.get(id = organization_pk )
	note = OrganizationUser.objects.get( user_id = user_pk , organization_id = organization_pk ).delete()
	print note
	#OrganizationUser.objects.create(user=user,organization=organization)
	return HttpResponseRedirect('/groups/')
	
