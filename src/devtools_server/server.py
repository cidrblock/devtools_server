"""Django server for the devtools API."""

from __future__ import annotations

import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application
from django.urls import path

from .creator import CreatorFrontendV1


DEBUG = os.environ.get("DEBUG", "on") == "on"
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))


settings.configure(
    DEBUG=DEBUG,
    SECRET_KEY=SECRET_KEY,
    ALLOWED_HOSTS=[
        "*",
    ],
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ),
)


urlpatterns = (
    path(route="v1/creator/playbook", view=CreatorFrontendV1().playbook),
    path(route="v1/creator/collection", view=CreatorFrontendV1().collection),
)


application = get_wsgi_application()


def main(args: list[str] | None = None) -> None:
    """Run the server."""
    if args is None:
        args = sys.argv
    execute_from_command_line(args)


if __name__ == "__main__":
    main()
