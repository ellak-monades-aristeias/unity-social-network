from django.contrib import admin
from .models import Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'id', 'type', 'desc', )
    list_editable = ('id', 'type', 'desc', )

