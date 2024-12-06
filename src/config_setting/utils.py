from typing import Any, Optional, Callable, TypeVar, Union

from decouple import config as decouple_config
from dotenv import load_dotenv

from src.config_setting import service as config_setting_service
from src.database import GetDB

load_dotenv()

T = TypeVar("T")


def get_config(
    key: str,
    default: Any = None,
    cast: Optional[Callable[[Any], T]] = None,
) -> Union[T, Any]:
    """
    Get configuration value with better type casting and None handling.

    Args:
        key: The configuration key to look up
        default: Default value if key is not found or value is invalid
        cast: Optional function to cast the value to a specific type
    """
    try:
        value = decouple_config(key, default=None)

        # Handle cases where value is None or 'None' string
        if value is None or (isinstance(value, str) and value.lower() == "none"):
            return default

        # Now value is not None, handle casting
        if cast is None:
            return value

        # Special handling for boolean values
        if cast is bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on", "t")
            return bool(value)

        # Try to cast the value
        try:
            return cast(value)
        except (ValueError, TypeError):
            return default

    except Exception:
        return default


def get_setting(key: str, default: Any = None, cast: Optional[type] = None) -> Any:
    """
    Get configuration value with database override capability.
    First checks database, falls back to environment variables if not found.

    Args:
        key: Configuration key to look up
        default: Default value if key is not found
        cast: Optional type casting function
    """

    value = None

    # Try to get from database first
    try:
        with GetDB() as db:
            value = config_setting_service.get_setting(db, key, cast)
    except Exception:
        pass

    # If not in database, fall back to environment
    if value is None:
        value = get_config(key, default, cast)

    return value
