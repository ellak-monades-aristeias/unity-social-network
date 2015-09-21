from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.edit import FormView
from django.shortcuts import redirect, render
from roles.models import Role
from roles.forms import RoleForm
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory


class RoleView(FormView):
    template_name = 'role/form.html'
    form_class = RoleForm

@login_required
def init(request):
    if request.user.is_superuser:

        roles_count = Role.objects.all().count()
        print roles_count

        if roles_count == 0:
            RoleFormSet = formset_factory(RoleForm, extra=2)
            print RoleFormSet
            if request.method == 'POST':
                return HttpResponse('<h1>In post form</h1>')
            else:
                #role_formset = RoleFormSet
                context = {
                 'role_formset': RoleFormSet,
                }
                return render(request, 'setup/init_roles.html', context)

        else:
            return HttpResponse('<h1>Roles found</h1>')
    else:
        return HttpResponse('<h1>Super Admin Login Required</h1>')