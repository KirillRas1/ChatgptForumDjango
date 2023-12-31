from rest_framework.permissions import BasePermission

RETRIEVE_METHODS = ["GET", "HEAD", "OPTIONS"]
CREATE_METHODS = ["POST", "PUT"]
REDACT_DESTROY_METHODS = ["PATCH", "DELETE"]


def allow_any(*args, **kwargs):
    return True


def allow_authenticated(request, *args, **kwargs):
    return request.user.is_authenticated


def allow_owner(request, view, **kwargs):
    owner_field = view.queryset.model.owner_field()
    filter_kwargs = {**view.kwargs, f"{owner_field}": request.user}
    view_queryset = view.get_queryset().filter(**filter_kwargs)

    #   Only works if for the queryset there is only one owner.
    #   Check if there is only one owner to the queryset
    if owner_field != "id":
        owners_list_query = view_queryset.values(owner_field)
        single_owner_in_query = owners_list_query.distinct().count() == 1
    else:
        single_owner_in_query = view_queryset.count() == 1
    if not single_owner_in_query:
        return False

    #   Check that the single owner of the queryset is the user
    if owner_field != "id":
        is_owner = (
            getattr(view_queryset.first(), owner_field) == request.user
        )  # For models with FK owner_field
    else:
        is_owner = (
            view_queryset.first() == request.user
        )  # For models with PK owner_field

    return request.user.is_authenticated and is_owner and single_owner_in_query


def handle_request(request, view):
    handlers = {
        **dict.fromkeys(RETRIEVE_METHODS, allow_any),
        **dict.fromkeys(CREATE_METHODS, allow_authenticated),
        **dict.fromkeys(REDACT_DESTROY_METHODS, allow_owner),
    }
    return handlers.get(request.method, lambda method: False)(request, view)


class AllowBasedOnMethod(BasePermission):
    """
    1. Allows read methods to any user
    2. Allows creation methods to authenticated users
    3. Allows redaction methods to owners
    """

    def has_permission(self, request, view):
        return handle_request(request, view)


class AllowOwner(BasePermission):
    """
    Allow only owner to do anything.
    """

    def has_permission(self, request, view):
        return allow_owner(request, view)
