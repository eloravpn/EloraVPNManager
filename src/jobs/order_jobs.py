from datetime import datetime, timedelta

from src import scheduler, logger, config
from src.accounts.schemas import AccountCreate, AccountModify
from src.accounts.service import (
    create_account,
    reset_traffic,
    update_account,
)
from src.commerce.schemas import OrderStatus
from src.commerce.service import get_orders, update_order_status
from src.database import GetDB
from src.telegram import utils
from src.telegram.utils import get_random_string


def process_paid_orders():
    logger.info("Process Paid Orders")

    with GetDB() as db:
        for db_order in get_orders(
            db=db, status=OrderStatus.paid, return_with_count=False
        ):
            try:
                logger.info(f"Process order with id: {db_order.id}")
                if db_order.service_id:
                    db_service = db_order.service
                    db_account = db_order.account
                    db_user = db_order.user
                    db_host_zone = db_order.host_zone

                    today = datetime.now()
                    expired_at = today + timedelta(days=db_order.duration)

                    if db_account:
                        if db_account.enable:
                            logger.info("Account is enable, Skip to recharge now!")
                        else:
                            logger.info(f"Recharge account {db_account.email}")

                            reset_traffic(db=db, db_account=db_account)

                            account_modify = AccountModify(
                                id=db_account.id,
                                user_id=db_account.user_id,
                                host_zone_id=db_host_zone.id,
                                uuid=db_account.uuid,
                                data_limit=db_order.data_limit,
                                ip_limit=db_order.ip_limit,
                                email=db_account.email,
                                enable=True,
                                expired_at=expired_at,
                            )

                            db_account = update_account(
                                db=db,
                                db_account=db_account,
                                modify=account_modify,
                                db_host_zone=db_host_zone,
                            )

                            update_order_status(
                                db=db,
                                db_order=db_order,
                                db_account=db_account,
                                status=OrderStatus.completed,
                            )

                    else:
                        logger.info(f"Create new account")

                        account = AccountCreate(
                            host_zone_id=db_host_zone.id,
                            user_id=db_order.user_id,
                            ip_limit=db_order.ip_limit,
                            data_limit=db_service.data_limit,
                            email=get_random_string(6),
                            enable=True,
                            expired_at=expired_at,
                        )

                        db_account = create_account(
                            db=db,
                            db_user=db_user,
                            account=account,
                            db_host_zone=db_host_zone,
                        )

                        update_order_status(
                            db=db,
                            db_order=db_order,
                            db_account=db_account,
                            status=OrderStatus.completed,
                        )

                else:
                    # TODO
                    logger.warn("Not implemented yet")
            except Exception as error:
                utils.send_message_to_admin(
                    message=f"Error in process order {db_order.id}"
                )
                logger.error(error)


if config.ENABLE_ORDER_JOBS:
    scheduler.add_job(
        func=process_paid_orders,
        max_instances=1,
        trigger="interval",
        seconds=config.PROCESS_PAID_ORDERS_INTERVAL,
    )
else:
    logger.warn("Order JOBS are disabled!")
