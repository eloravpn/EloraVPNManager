import json
from datetime import datetime
from typing import Optional, Any

from sqlalchemy.orm import Session

from .models import ConfigSetting


def get_all_setting(db: Session) -> Optional[Any]:
    """List all configurations"""
    settings = db.query(ConfigSetting).all()
    return settings


def get_setting(db: Session, key: str, cast: Optional[type] = None) -> Optional[Any]:
    """Get a configuration value from database"""

    # Query database
    setting = db.query(ConfigSetting).filter(ConfigSetting.key == key).first()
    if setting:
        try:
            if cast:
                return cast(setting.value)
            else:
                value = deserialize_value(setting.value, setting.value_type)
            return value
        except:
            return None
    return None


def set_setting(db: Session, key: str, value: Any) -> None:
    """Set a configuration value in database"""
    value_type = get_value_type(value)
    serialized_value = serialize_value(value)

    setting = db.query(ConfigSetting).filter(ConfigSetting.key == key).first()
    if setting:
        setting.value = serialized_value
        setting.value_type = value_type
        setting.updated_at = datetime.utcnow()
    else:
        setting = ConfigSetting(key=key, value=serialized_value, value_type=value_type)
        db.add(setting)

    db.commit()


def delete_setting(db: Session, key: str) -> bool:
    """Delete a configuration value from database"""
    setting = db.query(ConfigSetting).filter(ConfigSetting.key == key).first()
    if setting:
        db.delete(setting)
        db.commit()
        return True
    return False


def get_value_type(value: Any) -> str:
    """Determine the type of a value"""
    if value is None:
        return "none"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, (list, tuple)):
        return "list"
    elif isinstance(value, dict):
        return "dict"
    return "str"


def serialize_value(value: Any) -> str:
    """Serialize value for storage"""
    if value is None:
        return "None"
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return str(value)


def deserialize_value(value: str, value_type: str) -> Any:
    """Deserialize value from storage"""
    if value_type == "none" or value == "None":
        return None
    elif value_type == "bool":
        return value.lower() in ("true", "1", "yes", "on", "t")
    elif value_type == "int":
        return int(value)
    elif value_type == "float":
        return float(value)
    elif value_type in ("list", "dict"):
        return json.loads(value)
    return value
