from rest_framework import exceptions
from rest_framework.permissions import BasePermission


class ModelPermissions(BasePermission):
    """
    The request is authenticated using `django.contrib.auth` permissions.
    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions

    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete` permissions on the model.

    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """

    perms_map = {
        'GET': '%(app_label)s.view_%(model_name)s',
        'OPTIONS': None,
        'HEAD': None,
        'POST': '%(app_label)s.add_%(model_name)s',
        'PUT': '%(app_label)s.change_%(model_name)s',
        'PATCH': '%(app_label)s.change_%(model_name)s',
        'DELETE': '%(app_label)s.delete_%(model_name)s',
    }

    authenticated_users_only = True

    def get_required_permission(self, method, model_cls):
        """
        Given a model and an HTTP method, return the permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        perm = self.perms_map[method]

        return perm and perm % kwargs

    def _queryset(self, view):
        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            return queryset

        return view.queryset

    def has_permission(self, request, view):
        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)

        if not queryset:
            return True

        perm = self.get_required_permission(request.method, queryset.model)

        if not perm:
            return True

        return request.user.has_perm(perm) or request.user.has_perm(f'{perm}_owned')

    def has_object_permission(self, request, view, obj):
        queryset = self._queryset(view)
        user = request.user

        if not queryset:
            return True

        perm = self.get_required_permission(request.method, queryset.model)

        return user.has_perm(perm) or user.has_perm(f'{perm}_owned') and hasattr(obj, 'owner') and obj.owner == user
