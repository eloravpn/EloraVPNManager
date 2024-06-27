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

🎁 هدیه دعوت از کاربر {full_name} برای پیوستن به جمع ما.

✳️ کافیه ما رو به دوستان بیشتری معرفی کنی تا هدیه های بیشتری دریافت کنی!
"""

PAYMENT_METHODS = {
    PaymentMethod.money_order.value: "کارت به کارت",
    PaymentMethod.online.value: "آنلاین",
    PaymentMethod.cryptocurrencies.value: "ارز دیجیتال",
}

TRANSACTION_DEPOSIT_NOTIFICATION = """
➕ افزایش موجودی حساب به مبلغ <code>{amount}</code> تومان
 
{description}"""

TRANSACTION_WITHDRAW_NOTIFICATION = """
➖ برداشت از حساب به مبلغ <code>{amount}</code> تومان {description}"""

ORDER_PAID_NOTIFICATION = """
✅ سفارش {title} با شناسه <code>{id}</code> با موفقیت پرداخت شد.
"""

ORDER_COMPLETE_NOTIFICATION = """
✅ سفارش {title} با شناسه <code>{id}</code> با موفقیت اعمال شد.
"""

USER_NOTIFICATION_ACCOUNT_EXTENDED = """

✅  ترافیک سرویس شما با آیدی {id} به میزان {extend_data_limit_gb}  گیگابایت و مدت زمان سرویس {extend_day} روز افزایش یافت.

<a href="https://t.me/{admin_id}">💬 ارتباط با پشتیبانی</a>
"""
