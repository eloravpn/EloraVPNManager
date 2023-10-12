from typing import Optional


class EloraApplicationError(Exception):
    """Generic error class."""

    _message: Optional[str] = None

    def message(self) -> str:
        if self._message:
            return self._message
        else:
            return self.__str__()
