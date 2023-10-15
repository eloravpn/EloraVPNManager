REGIATER_SUCCESS = """
درخواست شما برای ایجاد حساب کاربری با موفقیت ثبت شد 🎉

در صورت پرداخت هزینه اشتراک ماهیانه 🎁 اکانت اختصاصی شما از همین طریق برای شما ارسال خواهد شد 🍻
"""
REGISTER_ADMIN_ALERT = """
{} with Chat ID <code>{}</code> has requested to create a VPN user acoount.
"""
WELCOME_MESSAGE = """
سلام دوست عزیز 👋

از طریق این ربات می توانید در هر لحظه اقدام به خرید سرویس VPN جدید نمایید.

همچنین از طریق منوی زیر می توانید به اطلاعات پروفایل و وضعیت سرویس های خریداری شده خود دسترسی داشته باشید.

در صورت داشتن هرگونه پرسشی از لینک زیر جهت ارتباط با ادمین استفاده نمایید.

💬 [ارتباط با ادمین](https://t.me/{}) / 📣 [کانال تلگرام](https://t.me/EloraVPNChannel/73)

"""

PLEASE_SUBSCRIBE_MESSAGE = """
سلام دوست عزیز 👋

📌 لطفا برای تجربه بهتر استفاده از ربات، اطلاع رسانی ها و همچنین تخفیف در کانال ما عضو شوید.

👈🏻 پس از عضویت روی دکمه ( ✅ عضو شدم ) کلیک کنید
"""

MY_ACCOUNT_MESSAGE = """
 وضعیت: {}
 شناسه سرویس: <code>{}</code>

شما تاکنون {} از {}، معادل {} درصد ترافیک سرویس خود را مصرف نموده اید.

⏰ تاریخ اعتبار : {}

⚠️ از ارسال این لینک در پیامک یا پیام رسان های داخلی خودداری نمایید، زیرا باعث غیرفعال شدن اکانت شما خواهد شد.

روی متن زیر کلیک نمایید تا لینک اشتراک پروفایل شما در کلیپ بورد کپی شود: 
 
 <code>{}/{}</code>
"""

ACCOUNT_LIST_MESSAGE = """

در این قسمت لیست سرویس های شما قابل مشاهده می باشد.
جهت دسترسی به جزییات هر سرویس روی نام آن کلیک نمایید.


"""

NO_ACCOUNT_MESSAGE = """
شما سرویس فعالی ندارید، لطفا از قسمت خرید سرویس اقدام به خرید یک سرویس نمایید.
"""

NOT_IMPLEMENTED = """

این امکان بزودی اضافه خواهد شد.


"""

BUY_NEW_SERVICE_HELP = """
لطفا یکی از سرویس های زیر را جهت خرید انتخاب نمایید:
"""

USAGE_HELP_MESSAGE = """
⚠️ از ارسال لینک اشتراک در پیامک یا پیام رسان های داخلی خودداری نمایید، زیرا باعث غیرفعال شدن اکانت شما خواهد شد.

لطفا تمامی مراحل موجود در کلیپ های آموزشی را با دقت انجام دهید تا بهترین سرعت را دریافت نمایید.

سرویس VPN را روی چه دستگاهی می خواهید استفاده نمایید؟


"""

PRICE_LIST = """
جهت مشاهده لیست تعرفه سرویس ها روی لینک زیر ضربه بزنید.
<a href="https://t.me/EloraVPNChannel/102"> 🛍 لیست تعرفه سرویس</a>
"""

MY_PROFILE = """
مشخصات:{full_name}
موجودی حساب: {balance} تومان

"""

ONLINE_PAYMENT_IS_DISABLED = """
پرداخت آنلاین به صورت موقت غیرفعال است، لطفا از روش کارت به کارت استفاده نمایید.
"""

BUY_NEW_SERVICE_CONFIRMATION = """
آیا با ثبت سفارش جهت <b> خرید {} به مبلغ {} تومان </b> موافقید؟
"""

BUY_NEW_SERVICE_FINAL = """
سفارش شما با شناسه <code>{}</code> با موفقیت ثبت شد.
( با کلیک روی عدد بالا، شناسه سفارش در کلیپ بورد شما کپی خواهد شد)

1️⃣ می توانید از طریق دکمه پرداخت آنلاین هزینه سرویس را پرداخت نمایید.
<i> توجه کنید که شناسه سفارش را در صفحه پرداخت آنلاین در قسمت شناسه سفارش به درستی وارد نمایید. </i>

2️⃣ اگر مایل به پرداخت به روش کارت به کارت هستید لطفا به ادمین پیام دهید.

✅ پس از پرداخت هزینه، سرویس شما در قسمت سرویس های من فعال خواهد شد.
<a href="https://t.me/{}">💬 ارتباط با ادمین</a>

"""

NEW_ORDER_ADMIN_ALERT = """
#خرید_جدید
شناسه سفارش: <code>{}</code>
آیدی کاربر: <code>{}</code>
کاربر: <a href="tg://user?id={}">{}</a>

<b> خرید  {} </b>
"""

NEW_ORDER_MAX_OPEN_ORDERS = """
شما {total} سفارش در وضعیت باز دارید،
قبل از درج سفارش جدید باید سفارش قبلی خود را پرداخت یا لغو نمایید.

<a href="https://t.me/{admin_id}">💬 ارتباط با ادمین</a>
"""


NEW_ORDER_NO_ENOUGH_BALANCE = """
⚠️موجودی حساب شما کافی نمی باشد.
ابتدا از قسمت افزایش موجودی، میزان موجودی حساب خود را افزایش دهید.

موجودی حساب شما: {balance} تومان

<a href="https://t.me/{admin_id}">💬 ارتباط با ادمین</a>
"""

GET_TEST_SERVICE_ADMIN_ALERT = """
#سرویس_تستی_جدید
کاربر: <a href="tg://user?id={chat_id}">{full_name}</a>
<b> .یک سرویس تستی جدید ایجاد شد </b>
"""

GET_TEST_SERVICE_NOT_ALLOWED = """
⚠️ کاربر گرامی، بدلیل دریافت سرویس تستی در {day} روز گذشته، در حال حاضر مجاز به دریافت سرویس تستی جدید نیستید.
 
️ می توانید از قسمت <b>🛍 خرید سرویس</b> اقدام به خرید سرویس نمایید یا از طریق منوی <b>💎 سرویس های من</b> می توانید به سرویس تستی خود دسترسی داشته باشید.

<a href="https://t.me/{admin_id}">💬 ارتباط با ادمین</a>
"""

GET_TEST_SERVICE_SUCCESS = """
✅ سرویس تستی شما با موفقیت ایجاد شد.

✴️ از طریق منوی <b>💎 سرویس های من</b> می توانید به سرویس تستی خود دسترسی داشته باشید.

❇️ همچنین از منوی راهنما می توانید راهنمای اتصال مربوط به دستگاه خود را مشاهده نمایید و بر اساس کلیپ های آموزشی متصل شوید.

<b>قبلا از بروز بودن تمامی نرم افزار های دستگاه خود و سرعت اینترنت مطمئن شوید.</b>
<a href="https://t.me/{admin_id}">💬 ارتباط با ادمین</a>
"""

ADMIN_NOTIFICATION_USER_EXPIRED = """
اکانت با ایمیل {email} بدلیل {due} به مالکیت {full_name} منقضی شد.

<a href="https://t.me/{telegram_user_name}">{full_name}</a>

"""

USED_TRAFFIC_NOTIFICATION = """
⚠️ شما تا این لحظه بیش از {used_traffic_percent} درصد از ترافیک سرویس خود را مصرف نموده اید.

✳️ جهت مشاهده میزان ترافیک مصرفی و همچنین تاریخ انقضا سرویس، به منوی <b>💎 سرویس های من</b> مراجعه نمایید.

✴️ جهت تمدید سرویس می توانید از طریق منوی<b> 🛍 خرید سرویس</b> اقدام نمایید.

<a href="https://t.me/{admin_id}">💬 ارتباط با ادمین</a>
"""

EXPIRE_TIME_NOTIFICATION = """
⚠️ کمتر از {days} روز دیگر زمان اعتبار سرویس شما به پایان می رسد.

✳️ جهت مشاهده میزان ترافیک مصرفی و همچنین تاریخ انقضا سرویس، به منوی <b>💎 سرویس های من</b> مراجعه نمایید.

✴️ جهت تمدید سرویس می توانید از طریق منوی<b> 🛍 خرید سرویس</b> اقدام نمایید.

<a href="https://t.me/{admin_id}">💬 ارتباط با ادمین</a>
"""
