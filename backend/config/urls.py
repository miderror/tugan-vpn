from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .routing import scoped_middleware

urlpatterns = [
    path(
        "admin/", include(scoped_middleware(settings.ADMIN_MIDDLEWARE, admin.site.urls))
    ),
    path("api/v1/", include("api.v1.router")),
]
