class MaxOpenOrderError(Exception):
    """Exception raised for users that have too many open orders

    Attributes:
        total -- Total open orders
        message -- explanation of the error
    """

    def __init__(self, total: int = 1):
        self.total = total
        self.message = f"There are {total} open orders right now"
        super().__init__(self.message)


class MaxPendingOrderError(Exception):
    """Exception raised for users that have too many open orders

    Attributes:
        total -- Total pending orders
        message -- explanation of the error
    """

    def __init__(self, total: int = 1):
        self.total = total
        self.message = f"There are {total} pending orders right now"
        super().__init__(self.message)


class NoEnoughBalanceError(Exception):
    """Exception raised when user don't have enough balance to place paid order

    Attributes:
        total -- Total
        message -- explanation of the error
    """

    def __init__(self, total: int = 0, balance: int = 0):
        self.total = total
        self.balance = balance
        self.message = f"Total orders is {total}"
        super().__init__(self.message)
