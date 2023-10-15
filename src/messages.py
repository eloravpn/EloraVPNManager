from src.commerce.schemas import PaymentMethod

TRANSACTION_INCREASE_BALANCE = """
افزایش موجودی حساب  به مبلغ {total} تومان از طریق پرداخت به روش {method}
"""

PAYMENT_METHODS = {
    PaymentMethod.money_order.value: "کارت به کارت",
    PaymentMethod.online.value: "آنلاین",
    PaymentMethod.cryptocurrencies.value: "ارز دیجیتال",
}
