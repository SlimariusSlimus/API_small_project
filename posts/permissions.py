from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow authors of an object to edit or delete it"""
    def has_object_permission(self, request, view, obj):
        # read permissions are allowed to any request so we always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # write permissions are only allowed to the author of the post or comment
        # obj.author refers to the author field in the Post and Comment models
        # here it is compared with the user who requested the change
        return obj.author == request.user
