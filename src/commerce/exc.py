from src.exc import EloraApplicationError


class MaxOpenOrderError(EloraApplicationError, Exception):
    """Exception raised for users that have too many open orders

    Attributes:
        total -- Total open orders
        message -- explanation of the error
    """

    def __init__(self, total: int = 1):
        self.total = total
        self._message = f"There are {total} open orders right now"
        super().__init__(self.message)


class MaxPendingOrderError(EloraApplicationError, Exception):
    """Exception raised for users that have too many open orders

    Attributes:
        total -- Total pending orders
        message -- explanation of the error
    """

    def __init__(self, total: int = 1):
        self._message = f"There are {total} pending orders right now"
        super().__init__(self._message)


class OrderNotEditableError(EloraApplicationError, Exception):
    """Exception raised when order not editable

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, total: int = 1):
        self._message = f"Order is not editable"
        super().__init__(self._message)


class OrderStatusConflictError(EloraApplicationError, Exception):
    """Exception raised when the new status is not valid

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, total: int = 1):
        self._message = f"Could not set this status"
        super().__init__(self._message)


class NoEnoughBalanceError(EloraApplicationError, Exception):
    """Exception raised when user don't have enough balance to place paid order

    Attributes:
        total -- Total
        message -- explanation of the error
    """

    def __init__(self, total: int = 0):
        self._message = f"Not enough balance to place PAID order with total: {total}"
        super().__init__(self._message)


class PaymentPaidStatusError(EloraApplicationError, Exception):
    """Exception raised when a PAID payment modified

    Attributes:
        message -- explanation of the error
    """

    def __init__(self):
        self._message = f"Could not Modify PAID payment"
        super().__init__(self._message)
