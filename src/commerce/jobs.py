import requests
from apscheduler.triggers.cron import CronTrigger

import src.commerce.service as commerce_service
from src import scheduler, config
from src.commerce.schemas import CurrencySymbol, CurrencyCreate
from src.database import GetDB


def update_currencies_rate():

    url = f"https://api.nobitex.ir/market/stats?srcCurrency={CurrencySymbol.USDT.value}&dstCurrency={CurrencySymbol.RLS.value}"

    response = requests.get(
        url,
        verify=False,
        timeout=20,
    )

    if response.status_code == 200:
        data = response.json()
        rate = data["stats"]["usdt-rls"]["dayLow"]

        with GetDB() as db:
            db_currency = commerce_service.get_currency(
                db=db, symbol=CurrencySymbol.USDTRLS
            )

            if db_currency is None:
                currency = CurrencyCreate(rate=int(rate), symbol=CurrencySymbol.USDTRLS)

                commerce_service.create_currency(db, currency)
            else:
                commerce_service.update_currency_price(db, db_currency, int(rate))


scheduler.add_job(
    func=update_currencies_rate,
    max_instances=1,
    trigger=CronTrigger.from_crontab(config.UPDATE_CURRENCIES_RATE_CRON),
)
