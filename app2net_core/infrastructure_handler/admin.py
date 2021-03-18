from django.contrib import admin
from .models import *


class InterfaceInline(admin.TabularInline):
    model = Interface
    extra = 0


class DeviceAdmin(admin.ModelAdmin):
    inlines = [InterfaceInline]


admin.site.register(Address)
admin.site.register(AddressType)
admin.site.register(AccessType)
admin.site.register(Credential)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Driver)
admin.site.register(InstalledDriver)
admin.site.register(Link)
admin.site.register(Internal)
admin.site.register(External)
admin.site.register(ProgrammableTechnology)
admin.site.register(Pvn)
admin.site.register(Resource)
admin.site.register(ResourceType)
admin.site.register(Physical)
admin.site.register(Logical)
