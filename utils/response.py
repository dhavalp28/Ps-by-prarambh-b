from typing import Any, Dict, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API Response Model"""

    response: bool
    title: str
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None


class SuccessResponse:
    """Helper class to create success responses"""

    @staticmethod
    def create(
        title: str, data: Optional[Any] = None, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a success response

        Args:
            title: Response title/description
            data: Response data (can be list, dict, or any object)
            message: Optional success message

        Returns:
            Dictionary with standardized response format
        """
        return {
            "response": True,
            "title": title,
            "data": data,
            "message": message,
            "error": None,
        }


class ErrorResponse:
    """Helper class to create error responses"""

    @staticmethod
    def create(
        title: str,
        error: Optional[str],
        data: Optional[Any] = None,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an error response

        Args:
            title: Response title/description
            error: Error message/description
            data: Optional error data
            message: Optional additional message

        Returns:
            Dictionary with standardized error response format
        """
        return {
            "response": False,
            "title": title,
            "data": data,
            "message": message,
            "error": error,
        }


# Predefined response helpers for common scenarios


def success_list(
    title: str, data: Any, message: Optional[str] = None
) -> Dict[str, Any]:
    """Success response for list operations"""
    return SuccessResponse.create(title=title, data=data, message=message)


def success_create(
    title: str, data: Any, message: Optional[str] = None
) -> Dict[str, Any]:
    """Success response for create operations"""
    return SuccessResponse.create(
        title=title, data=data, message=message or "Created successfully"
    )


def success_update(
    title: str, data: Any, message: Optional[str] = None
) -> Dict[str, Any]:
    """Success response for update operations"""
    return SuccessResponse.create(
        title=title, data=data, message=message or "Updated successfully"
    )


def success_delete(
    title: str,
    resource_id: Optional[int] = None,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Success response for delete operations"""
    return SuccessResponse.create(
        title=title,
        data={"id": resource_id} if resource_id else None,
        message=message or "Deleted successfully",
    )


def error_not_found(title: str, resource: str = "Resource") -> Dict[str, Any]:
    """Error response for not found"""
    return ErrorResponse.create(title=title, error=f"{resource} not found")


def error_validation(title: str, error: str, data: Any = None) -> Dict[str, Any]:
    """Error response for validation errors"""
    return ErrorResponse.create(title=title, error=error, data=data)


def error_duplicate(title: str, resource: str = "Resource") -> Dict[str, Any]:
    """Error response for duplicate entries"""
    return ErrorResponse.create(title=title, error=f"{resource} already exists")


def error_server(
    title: str, error: Optional[str] = "Internal server error"
) -> Dict[str, Any]:
    """Error response for server errors"""
    return ErrorResponse.create(title=title, error=error)


def error_unauthorized(title: str = "Unauthorized") -> Dict[str, Any]:
    """Error response for unauthorized access"""
    return ErrorResponse.create(title=title, error="Unauthorized access")


def error_forbidden(title: str = "Forbidden") -> Dict[str, Any]:
    """Error response for forbidden access"""
    return ErrorResponse.create(title=title, error="Access forbidden")
