# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


from userprofiles.settings import up_settings

if up_settings.USE_PROFILE and up_settings.INLINE_PROFILE_ADMIN:
    from userprofiles.utils import UserProfile

    admin.site.unregister(User)

    class UserProfileInline(admin.StackedInline):
        model = UserProfile
        extra = 1
        max_num = 1

    class UserProfileAdmin(UserAdmin):
        inlines = [UserProfileInline]

    admin.site.register(User, UserProfileAdmin)


from userprofiles.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'role', 'displayName', )
    list_editable = ('user','role','displayName')

admin.site.register(UserProfile, UserProfileAdmin)
