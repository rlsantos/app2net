from rest_framework.permissions import IsAuthenticated


class UserOwnsObject(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.owners.filter(id=request.user.id).exists()
