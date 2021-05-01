from django.contrib import admin
from .models import Action, NetApp, NetAppPackage, Repository, Category


class ActionInline(admin.StackedInline):
    model = Action
    extra = 0
    min_num = 1


class NetworkServicePackageAdmin(admin.ModelAdmin):
    inlines = [ActionInline]


admin.site.register(NetApp)
admin.site.register(NetAppPackage, NetworkServicePackageAdmin)
admin.site.register(Repository)
admin.site.register(Category)
