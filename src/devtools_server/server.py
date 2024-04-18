"""Django server for the devtools API."""

from __future__ import annotations

import os
import sys
import tempfile

from importlib import resources as importlib_resources
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application
from django.http import FileResponse, HttpResponse
from django.urls import path
from openapi_core import OpenAPI
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.exceptions import OpenAPIError

from .creator import Creator


if TYPE_CHECKING:
    from django.http import HttpRequest
    from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


DEBUG = os.environ.get("DEBUG", "on") == "on"
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
OPENAPI = OpenAPI.from_dict(
    yaml.safe_load(
        importlib_resources.read_text("devtools_server.data", "openapi.yaml"),
    ),
)


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


def validate_request(request: HttpRequest) -> RequestUnmarshalResult | HttpResponse:
    """Validate the request against the OpenAPI schema.

    Args:
        request: HttpRequest object
    Returns:
        dict: The request body
        HttpResponse: The error response
    """
    try:
        openapi_request = DjangoOpenAPIRequest(request)
        OPENAPI.validate_request(openapi_request)
    except OpenAPIError as exc:
        return HttpResponse(str(exc), status=400)
    return OPENAPI.unmarshal_request(openapi_request)


def creator_playbook(request: HttpRequest) -> FileResponse | HttpResponse:
    """Create a new playbook project.

    Args:
        request: HttpRequest object
    Returns:
        File or error response
    """
    result = validate_request(request)
    if isinstance(result, HttpResponse):
        return result
    with tempfile.TemporaryDirectory() as tmp_dir:
        # result.body here is a dict, it appear the type hint is wrong
        tar_file = Creator(Path(tmp_dir)).playbook(**result.body)  # type: ignore[arg-type]
        fs = FileSystemStorage(tmp_dir)
        response = FileResponse(
            fs.open(str(tar_file), "rb"),
            content_type="application/tar+gzip",
            status=201,
        )
        response["Content-Disposition"] = f'attachment; filename="{tar_file.name}"'

    # File response is a subclass of StreamingHttpResponse, but nearly identical
    # https://docs.djangoproject.com/en/5.0/ref/request-response/#django.http.StreamingHttpResponse

    OPENAPI.validate_response(
        request=DjangoOpenAPIRequest(request),
        response=DjangoOpenAPIResponse(response),  # type: ignore[arg-type]
    )

    return response


def create_collection(request: HttpRequest) -> FileResponse | HttpResponse:
    """Create a new collection project.

    Args:
        request: HttpRequest object
    Returns:
        File or error response
    """
    result = validate_request(request)
    if isinstance(result, HttpResponse):
        return result
    with tempfile.TemporaryDirectory() as tmp_dir:
        # result.body here is a dict, it appear the type hint is wrong
        tar_file = Creator(Path(tmp_dir)).collection(**result.body)  # type: ignore[arg-type]
        fs = FileSystemStorage(tmp_dir)
        response = FileResponse(
            fs.open(str(tar_file), "rb"),
            content_type="application/tar+gzip",
            status=201,
        )
        response["Content-Disposition"] = f'attachment; filename="{tar_file.name}"'

    # File response is a subclass of StreamingHttpResponse, but nearly identical
    # https://docs.djangoproject.com/en/5.0/ref/request-response/#django.http.StreamingHttpResponse

    OPENAPI.validate_response(
        request=DjangoOpenAPIRequest(request),
        response=DjangoOpenAPIResponse(response),  # type: ignore[arg-type]
    )

    return response


urlpatterns = (
    path(route="v1/creator/playbook", view=creator_playbook),
    path(route="v1/creator/collection", view=create_collection),
)


app = get_wsgi_application()


def main() -> None:
    """Run the server."""
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
