from datetime import datetime
from typing import Any, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(
    status_code: int = status.HTTP_200_OK,
    detail: str = "",
    data: Any = None,
    previous_page: Optional[int] = None,
    current_page: Optional[int] = None,
    next_page: Optional[int] = None,
    total_pages: Optional[int] = None,
    total: Optional[int] = None,
    is_paginated: bool = False,
) -> JSONResponse:
    """
    Generates a success response dictionary with the provided parameters.

    Args:
        status_code (int): The HTTP status code for the response. Default is 200.
        detail (str): Additional details about the response. Default is an empty string.
        data (Any): The data to be included in the response. Default is an empty dictionary.
        previous_page (Optional[int]): The page number of the previous page in a paginated response. Default is None.
        current_page (Optional[int]): The page number of the current page in a paginated response. Default is None.
        next_page (Optional[int]): The page number of the next page in a paginated response. Default is None.
        total_pages (Optional[int]): The total number of pages in a paginated response. Default is None.
        total (Optional[int]): The total number of items in a paginated response. Default is None.
        is_paginated (bool): Indicates whether the response is paginated. Default is False.

    Returns:
        JSONResponse: A success response object.
    """
    content = {
        "status_code": status_code,
        "detail": detail,
        "data": jsonable_encoder(data)
    }

    if is_paginated:
        content.update(
            {
                "previous_page": previous_page,
                "current_page": current_page,
                "next_page": next_page,
                "total_pages": total_pages,
                "total": total
            }
        )

    return JSONResponse(status_code=status_code, content=content)


def error_response(
    detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> JSONResponse:
    """
    Generates an error response with the specified detail and status code.

    Args:
        detail (str): The error message or details.
        status_code (int, optional): The HTTP status code to be returned. Defaults to 500.

    Returns:
        JSONResponse: The error response object.

    """
    content = {
        "status_code": status_code,
        "detail": detail
        }
    response = JSONResponse(status_code=status_code, content=content)
    return response


def time_now() -> datetime:
    """
    Returns the current datetime.

    Returns:
        datetime: The current datetime.
    """
    return datetime.now()