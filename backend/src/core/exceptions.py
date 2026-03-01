"""Custom exception classes for OptiMeal API."""
from typing import Any, Dict, Optional


class OptiMealException(Exception):
    """Base exception for OptiMeal application."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(OptiMealException):
    """Exception for database-related errors."""

    def __init__(self, message: str = "Database error occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class AuthenticationError(OptiMealException):
    """Exception for authentication failures."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(OptiMealException):
    """Exception for authorization failures."""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(OptiMealException):
    """Exception for resource not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(OptiMealException):
    """Exception for validation errors."""

    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class OptimizationError(OptiMealException):
    """Exception for optimization algorithm errors."""

    def __init__(self, message: str = "Optimization failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class DishConstraintError(OptiMealException):
    """Exception for dish-based constraint violations."""

    def __init__(self, message: str = "Dish constraint violation", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


