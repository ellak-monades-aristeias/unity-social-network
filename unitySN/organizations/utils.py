from organizations.models import (Organization, OrganizationUser,
        OrganizationOwner)
import datetime  

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now  


def create_organization(user, name, description, image, is_active=True):
    """
    Returns a new organization, also creating an initial organization user who
    is the owner.
    """
    organization = Organization.objects.create(name=name.encode('utf-8'), description = description.encode('utf-8'),image = image.encode('utf-8'),is_active=is_active  )
    new_user = OrganizationUser.objects.create(organization=organization,
            user=user, is_admin=True)
    OrganizationOwner.objects.create(organization=organization,
            organization_user=new_user )
    return organization


def model_field_attr(model, model_field, attr):
    """
    Returns the specified attribute for the specified field on the model class.
    """
    fields = dict([(field.name, field) for field in model._meta.fields])
    return getattr(fields[model_field], attr)
