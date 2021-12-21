from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.gis.admin import GISModelAdmin

from .models import Client, Item, ClientUser, ItemFile


# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    pass


admin.site.register(Client, ClientAdmin)


class ItemFileInline(admin.TabularInline):
    model = ItemFile


class ItemAdmin(GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 37.618423,
            'default_lat': 55.751244,
            'default_zoom': 14
        }
    }

    list_display = ('id', 'client', 'name', 'total_area')
    list_filter = ('client',)

    inlines = [
        ItemFileInline,
    ]


admin.site.register(Item, ItemAdmin)


# Redefine users admin
class ClientUserInline(admin.StackedInline):
    model = ClientUser
    can_delete = False
    verbose_name_plural = 'Client Users'
    filter_horizontal = ('client',)


class UserAdmin(BaseUserAdmin):
    inlines = (ClientUserInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
