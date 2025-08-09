from itertools import filterfalse

from wagtail import hooks
from wagtail_localize import wagtail_hooks as localize_hooks


def unregister(hook_name, func):
    registered_funcs = hooks._hooks.get(hook_name)
    if registered_funcs:
        hooks._hooks[hook_name] = list(filterfalse(lambda x: x[0] == func, registered_funcs))


unregister("register_page_header_buttons", localize_hooks.page_listing_more_buttons)
unregister("register_page_listing_more_buttons", localize_hooks.page_listing_more_buttons)
