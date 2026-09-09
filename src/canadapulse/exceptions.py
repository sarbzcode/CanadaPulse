"""Domain exceptions used across CanadaPulse."""


class CanadaPulseError(Exception):
    """Base exception for CanadaPulse application errors."""


class ConfigurationError(CanadaPulseError):
    """Raised when runtime configuration is invalid."""


class DatabaseConnectionError(CanadaPulseError):
    """Raised when the application cannot connect to PostgreSQL."""


class PipelineMetadataError(CanadaPulseError):
    """Raised when pipeline metadata cannot be recorded."""

