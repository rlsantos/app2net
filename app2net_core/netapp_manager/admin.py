from django.contrib import admin
from .models import Action, NetworkService, NetworkServicePackage, Repository


class ActionInline(admin.StackedInline):
    model = Action
    extra = 0
    min_num = 1


class NetworkServicePackageAdmin(admin.ModelAdmin):
    inlines = [ActionInline]


admin.site.register(NetworkService)
admin.site.register(NetworkServicePackage, NetworkServicePackageAdmin)
admin.site.register(Repository)
