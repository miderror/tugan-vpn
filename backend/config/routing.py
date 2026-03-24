from django.utils.decorators import decorator_from_middleware
from django.utils.module_loading import import_string


def scoped_middleware(middleware_paths, url_conf):
    patterns, app_name, namespace = url_conf

    decorators = [
        decorator_from_middleware(import_string(path))
        for path in reversed(middleware_paths)
    ]

    for pattern in patterns:
        for decorator in decorators:
            pattern.callback = decorator(pattern.callback)

    return patterns, app_name, namespace
