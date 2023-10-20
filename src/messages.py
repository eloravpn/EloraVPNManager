from src.commerce.schemas import PaymentMethod

PAYMENT_PAID_DESCRIPTION = """
✳️ از طریق پرداخت با شناسه <code>{id}</code> به روش {method}
"""

USER_BALANCE = """
 💰 موجودی حساب: <code>{balance}</code> تومان
"""

ORDER_PAID_DESCRIPTION = """
✳️ از طریق سفارش شناسه <code>{id}</code>
"""

REFERRAL_BONUS_DESCRIPTION = """
🎉از طریق دعوت از دوستان
"""

PAYMENT_METHODS = {
    PaymentMethod.money_order.value: "کارت به کارت",
    PaymentMethod.online.value: "آنلاین",
    PaymentMethod.cryptocurrencies.value: "ارز دیجیتال",
}

TRANSACTION_DEPOSIT_NOTIFICATION = """
➕ افزایش موجودی حساب به مبلغ <code>{amount}</code> تومان {description}"""

TRANSACTION_WITHDRAW_NOTIFICATION = """
➖ برداشت از حساب به مبلغ <code>{amount}</code> تومان {description}"""

ORDER_PAID_NOTIFICATION = """
✅ سفارش {title} با شناسه <code>{id}</code> با موفقیت پرداخت شد.
"""

ORDER_COMPLETE_NOTIFICATION = """
✅ سفارش {title} با شناسه <code>{id}</code> با موفقیت اعمال شد.
"""
