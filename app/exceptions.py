class AIRouterException(Exception):
    """Base exception for AI Router"""

class ProviderNotFoundException(AIRouterException):
    """Raised when a provider is not found"""

class ModelNotFoundException(AIRouterException):
    """Raised when a model is not found"""

class AIGenerationException(AIRouterException):
    """Raised when there's an error generating AI response"""

class ConfigurationException(AIRouterException):
    """Raised when there's a configuration error"""
