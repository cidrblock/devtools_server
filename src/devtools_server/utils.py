"""Some utility functions."""

from importlib import resources as importlib_resources

import yaml

from django.http import FileResponse, HttpRequest, HttpResponse
from openapi_core import OpenAPI
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.exceptions import OpenAPIError
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


OPENAPI = OpenAPI.from_dict(
    yaml.safe_load(
        (importlib_resources.files("devtools_server.data") / "openapi.yaml").read_text(),
    ))


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


def validate_response(
    request: HttpRequest,
    response: HttpResponse | FileResponse,
) -> HttpResponse | FileResponse:
    """Validate the response against the OpenAPI schema.

    Args:
        request: HttpRequest object
        response: HttpResponse object
    """
    try:
        OPENAPI.validate_response(
            request=DjangoOpenAPIRequest(request),
            response=DjangoOpenAPIResponse(response),
        )
    except OpenAPIError as exc:
        return HttpResponse(str(exc), status=400)
    return response
