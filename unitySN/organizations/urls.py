from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from organizations.views import (OrganizationList, OrganizationDetail,
        OrganizationUpdate, OrganizationDelete, OrganizationCreate,
        OrganizationUserList, OrganizationUserDetail, OrganizationUserUpdate,
        OrganizationUserCreate, OrganizationUserRemind, OrganizationUserDelete)
        
from organizations import views


urlpatterns = patterns('',
    # Organization URLs
    url(r'^$', views.all_groups, name='all_groups'),
    url(r'^add/$', view=login_required(OrganizationCreate.as_view()),
        name="organization_add"),
    url(r'^(?P<organization_pk>[\d]+)/$',
        view=login_required(OrganizationDetail.as_view()),
        name="organization_detail"),
    url(r'^(?P<organization_pk>[\d]+)/edit/$',
        view=login_required(OrganizationUpdate.as_view()),
        name="organization_edit"),
    url(r'^(?P<organization_pk>[\d]+)/delete/$',
        view=login_required(OrganizationDelete.as_view()),
        name="organization_delete"),
   # url(r'^all/$', views.all_groups, name='all_groups' ),
    url(r'^(?P<organization_pk>[\d]+)/visit/$',  views.user_not_member, name='user_not_member'),
    url(r'^(?P<organization_pk>[\d]+)/add/(?P<user_pk>[\d]+)$',views.add_user,name="organization_user_add"),
    url(r'^(?P<organization_pk>[\d]+)/delete/(?P<user_pk>[\d]+)$',views.delete_user,name="organization_user_delete"),

    # Organization user URLs
    url(r'^(?P<organization_pk>[\d]+)/people/$',
        view=login_required(OrganizationUserList.as_view()),
        name="organization_user_list"),
    url(r'^(?P<organization_pk>[\d]+)/people/add/$',
        view=login_required(OrganizationUserCreate.as_view()),
        name="organization_user_add"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/remind/$',
        view=login_required(OrganizationUserRemind.as_view()),
        name="organization_user_remind"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/$',
        view=login_required(OrganizationUserDetail.as_view()),
        name="organization_user_detail"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/edit/$',
        view=login_required(OrganizationUserUpdate.as_view()),
        name="organization_user_edit"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/delete/$',
        view=login_required(OrganizationUserDelete.as_view()),
        name="organization_user_delete"),
)
