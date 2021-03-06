# Taken from Django 1.4

import warnings

from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.utils.decorators import decorator_from_middleware, available_attrs
from functools import wraps

csrf_protect = decorator_from_middleware(CsrfViewMiddleware)
csrf_protect.__name__ = "csrf_protect"
csrf_protect.__doc__ = """
This decorator adds CSRF protection in exactly the same way as
CsrfViewMiddleware, but it can be used on a per view basis.  Using both, or
using the decorator multiple times, is harmless and efficient.
"""


class _EnsureCsrfToken(CsrfViewMiddleware):
    # We need this to behave just like the CsrfViewMiddleware, but not reject
    # requests.
    def _reject(self, request, reason):
        return None


requires_csrf_token = decorator_from_middleware(_EnsureCsrfToken)
requires_csrf_token.__name__ = 'requires_csrf_token'
requires_csrf_token.__doc__ = """
Use this decorator on views that need a correct csrf_token available to
RequestContext, but without the CSRF protection that csrf_protect
enforces.
"""


class _EnsureCsrfCookie(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        retval = super(_EnsureCsrfCookie, self).process_view(request, callback, callback_args, callback_kwargs)
        # Forces process_response to send the cookie
        get_token(request)
        return retval


ensure_csrf_cookie = decorator_from_middleware(_EnsureCsrfCookie)
ensure_csrf_cookie.__name__ = 'ensure_csrf_cookie'
ensure_csrf_cookie.__doc__ = """
Use this decorator to ensure that a view sets a CSRF cookie, whether or not it
uses the csrf_token template tag, or the CsrfViewMiddleware is used.
"""


def csrf_response_exempt(view_func):
    """
    Modifies a view function so that its response is exempt
    from the post-processing of the CSRF middleware.
    """
    warnings.warn("csrf_response_exempt is deprecated. It no longer performs a "
                  "function, and calls to it can be removed.",
                  PendingDeprecationWarning)
    return view_func


def csrf_view_exempt(view_func):
    """
    Marks a view function as being exempt from CSRF view protection.
    """
    warnings.warn("csrf_view_exempt is deprecated. Use csrf_exempt instead.",
                  PendingDeprecationWarning)
    return csrf_exempt(view_func)


def csrf_exempt(view_func):
    """
    Marks a view function as being exempt from the CSRF view protection.
    """
    # We could just do view_func.csrf_exempt = True, but decorators
    # are nicer if they don't have side-effects, so we return a new
    # function.
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.csrf_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
