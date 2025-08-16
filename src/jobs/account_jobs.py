from datetime import datetime, timedelta

from src import scheduler, config
from src.logger import logger
from src.accounts.models import Account
from src.accounts.service import (
    get_accounts,
    update_account_status,
    remove_account,
    get_account_by_uuid_and_email,
    get_account_by_email,
    update_account_used_traffic,
    create_account_used_traffic,
)
from src.database import GetDB
from src.hosts.schemas import HostResponse
from src.hosts.service import get_host
from src.inbounds.service import get_inbounds
from src.middleware.x_ui import XUI
from src.notification.schemas import NotificationType, NotificationCreate
from src.notification.service import create_notification
from src.telegram.user import messages, captions
from src.users.models import User


def delete_client_in_all_inbounds(db, db_account: Account):
    inbounds, count = get_inbounds(db=db, enable=1)
    for inbound in inbounds:
        logger.info(f"Inbound Remark: {inbound.remark}")
        logger.info(f"Inbound Id: {inbound.id}")
        logger.info(f"Inbound host ID: {inbound.host_id}")

        if not inbound.enable or not inbound.host.enable:
            logger.info("Skip this inbound because it is disabled.")
            continue

        host = get_host(db, inbound.host_id)

        try:
            xui = XUI(host=HostResponse.from_orm(host))
        except Exception as error:
            logger.error(f"Could not connect to host {host.name} ")
            continue

        logger.info("Host name: " + host.name)

        account_unique_email = xui.api.get_account_email_prefix(
            inbound.key, db_account.email
        )

        logger.info(
            f"Account unique Email for this inbound is {account_unique_email} and uuid is {db_account.uuid}"
        )

        client_stat = xui.api.get_client_stat(email=account_unique_email)

        if client_stat is not None:
            deleted = xui.api.delete_client(
                inbound_id=inbound.key, uuid=db_account.uuid
            )
            if not deleted:
                logger.error("Error in delete account in this inbound!")
                raise Exception
            else:
                logger.info("Client Successfully deleted in this inbound!")
        else:
            logger.info(f"Client does not exist in this inbound yet")


def update_client_in_all_inbounds(db, db_account: Account, enable: bool = False):
    inbounds, count = get_inbounds(db=db, enable=1)
    for inbound in inbounds:
        logger.info(f"Inbound Remark: {inbound.remark}")
        logger.info(f"Inbound Id: {inbound.id}")
        logger.info(f"Inbound host ID: {inbound.host_id}")

        if not inbound.enable or not inbound.host.enable:
            logger.info("Skip this inbound because it is disabled.")
            continue

        host = get_host(db, inbound.host_id)

        try:
            xui = XUI(host=HostResponse.from_orm(host))
        except Exception as error:
            logger.error(f"Could not connect to host {host.name} ")
            continue

        logger.info("Host name: " + host.name)

        account_unique_email = xui.api.get_account_email_prefix(
            inbound.key, db_account.email
        )

        client_stat = xui.api.get_client_stat(email=account_unique_email)

        if client_stat is not None:
            # if client_stat["enable"] == enable:
            #     logger.info("This client is synced with account!")
            # else:
            xui.api.update_client(
                inbound_id=inbound.key,
                email=account_unique_email,
                uuid=db_account.uuid,
                enable=enable,
                ip_limit=db_account.ip_limit,
                flow=inbound.flow,
            )

        else:
            logger.info(f"Client does not exist in this inbound yet")


def clean_up_inbounds():
    logger.info("Start Cleanup Inbounds")
    start = datetime.utcnow().timestamp()

    with GetDB() as db:

        inbounds, count = get_inbounds(db=db, enable=1)
        for inbound in inbounds:
            try:
                logger.info(
                    f"Cleanup - Inbound Host: {inbound.host.name} and Inbound Remark: {inbound.remark} with key {inbound.key}"
                )

                if not inbound.enable or not inbound.host.enable:
                    logger.info("Skip this inbound because it is disabled.")
                    continue

                host = get_host(db, host_id=inbound.host_id)

                try:
                    xui = XUI(host=HostResponse.from_orm(host))
                except Exception as error:
                    logger.error(f"Could not connect to host {host.name} ")
                    continue

                remote_inbound_clients = xui.api.get_inbound_clients(inbound.key)

                if remote_inbound_clients is None:
                    logger.warn(
                        f"Remote clients is None in Inbound Remark: {inbound.remark} with key {inbound.key} in {host.name}"
                    )
                    continue

                for client in remote_inbound_clients:
                    client_email = client["email"]
                    uuid = client["id"]
                    enable = client["enable"]
                    account_email = xui.api.get_account_real_email(client_email)

                    logger.debug(f"Client Email: {client_email}")
                    logger.debug(f"Account Email: {account_email}")
                    logger.debug(f"Client UUID: {uuid}")
                    logger.debug(f"Client Status: {enable}")

                    if account_email is None:
                        logger.warn("This client is not handle with Elora Panel! Skip!")
                        continue

                    account = get_account_by_uuid_and_email(
                        db=db, uuid=uuid, email=account_email
                    )

                    if account:
                        if not account.enable and enable:
                            logger.info(
                                f"Try to Disable account with email {client_email}!"
                            )
                            xui.api.update_client(
                                inbound_id=inbound.key,
                                email=client_email,
                                uuid=uuid,
                                enable=False,
                                ip_limit=account.ip_limit,
                                flow=inbound.flow,
                            )

                        if account.enable and not enable:
                            logger.info(
                                f"Try to Enable account with email {client_email}!"
                            )
                            xui.api.update_client(
                                inbound_id=inbound.key,
                                email=client_email,
                                uuid=uuid,
                                enable=True,
                                ip_limit=account.ip_limit,
                                flow=inbound.flow,
                            )

                    if (
                        account is None
                        or account.host_zone_id != inbound.host.host_zone_id
                    ):
                        logger.warn(
                            f"Try to delete client with email {client_email} in this inbound!"
                        )
                        deleted = xui.api.delete_client(
                            inbound_id=inbound.key, uuid=uuid
                        )
                        if not deleted:
                            logger.error(
                                f"Error in delete account email {client_email} in this inbound!"
                            )
                        else:
                            logger.info(
                                f"Client email {client_email} Successfully deleted in this inbound!"
                            )

            except Exception as error:
                logger.error(error)
    end = datetime.utcnow().timestamp()
    logger.info(f"End Cleanup Inbounds in {end - start} Sec")


def sync_new_accounts():
    with GetDB() as db:
        logger.info("Start syncing new accounts in all inbounds")
        start = datetime.utcnow().timestamp()

        inbounds, count = get_inbounds(db=db, enable=1)
        for inbound in inbounds:
            logger.info(f"Host {inbound.host.name} Inbound Remark: {inbound.remark}")

            if not inbound.enable or not inbound.host.enable:
                logger.info("Skip this inbound because it is disabled.")
                continue

            host = get_host(db, host_id=inbound.host_id)

            try:
                xui = XUI(host=HostResponse.from_orm(host))
            except Exception as error:
                logger.error(f"Could not connect to host {host.name} ")
                continue

            remote_inbound_clients = xui.api.get_inbound_clients(inbound.key)

            if remote_inbound_clients is None:
                logger.warn(
                    f"Remote clients is None in Inbound Remark: {inbound.remark} with key {inbound.key} in {host.name}"
                )
                continue

            for account in get_accounts(
                db=db, return_with_count=False, filter_enable=True, enable=True
            ):
                # account_expire_time = account.expired_at.timestamp() * 1000s

                if not account.enable:
                    logger.debug("Account is disable, skipped to add!")
                    continue

                if account.host_zone_id != inbound.host.host_zone_id:
                    continue

                account_unique_email = xui.api.get_account_email_prefix(
                    inbound.key, account.email
                )

                if not any(
                    client.get("email", "") == account_unique_email
                    for client in remote_inbound_clients
                ):
                    logger.info(f"Try to add client in this inbound")
                    logger.info(f"Account uuid: {account.uuid}")
                    logger.info(f"Account email: {account.email}")
                    logger.info(f"Account Expire time: {account.expired_at}")

                    xui.api.add_client(
                        inbound_id=inbound.key,
                        email=account_unique_email,
                        uuid=account.uuid,
                        flow=inbound.flow.value if inbound.flow else "",
                        ip_limit=account.ip_limit,
                    )
        end = datetime.utcnow().timestamp()
        logger.info(f"End Sync new accounts in all Inbounds in {end - start} Sec")


def sync_accounts_traffic():
    with GetDB() as db:
        start = datetime.utcnow().timestamp()

        logger.info(
            "Start syncing accounts traffic from all inbounds " + str(datetime.now())
        )

        inbounds, count = get_inbounds(db=db, enable=1)
        for inbound in inbounds:
            try:

                host = get_host(db, inbound.host_id)

                logger.info(
                    f"Calculate client state in inbound {inbound.remark} with key {inbound.key} on {host.name}"
                )

                if not inbound.enable or not host.enable:
                    logger.info("Skip this inbound because it is disabled.")
                    continue

                xui = XUI(host=HostResponse.from_orm(host))

                remote_inbound_client_stats = xui.api.get_inbound_client_stats(
                    inbound.key
                )

                # db_accounts_used_traffic = []

                if remote_inbound_client_stats and len(remote_inbound_client_stats) > 0:
                    for client_stat in remote_inbound_client_stats:
                        client_email = client_stat["email"]
                        enable = client_stat["enable"]
                        account_email = xui.api.get_account_real_email(client_email)

                        logger.debug(f"Client Email: {client_email}")
                        logger.debug(f"Account Email: {account_email}")
                        logger.debug(f"Client Status: {enable}")

                        if account_email is None:
                            logger.warn(
                                "This client is not handle with Elora Panel! Skip!"
                            )
                            continue

                        db_account = get_account_by_email(db=db, email=account_email)

                        if db_account:
                            if not db_account.enable:
                                logger.debug(
                                    "Account is disable, skipped to update traffic!"
                                )
                                continue

                            download = (
                                int(client_stat["down"]) * config.GLOBAL_TRAFFIC_RATIO
                            )
                            upload = (
                                int(client_stat["up"]) * config.GLOBAL_TRAFFIC_RATIO
                            )

                            used_traffic = download + upload

                            if used_traffic > 0:
                                logger.debug(f"Client Upload: {upload}")
                                logger.debug(f"Client Download: {download}")
                                logger.debug(
                                    f"Client total usage: {used_traffic} with ratio {config.GLOBAL_TRAFFIC_RATIO}"
                                )

                                reset = xui.api.reset_client_traffic(
                                    inbound_id=inbound.key, email=client_email
                                )

                                if reset:
                                    create_account_used_traffic(
                                        db=db,
                                        db_account=db_account,
                                        upload=upload,
                                        download=download,
                                    )
                                    update_account_used_traffic(
                                        db=db,
                                        db_account=db_account,
                                        used_traffic=used_traffic
                                        + db_account.used_traffic,
                                    )
                                    logger.info(
                                        f"Traffic updated and reset successfully in {inbound.remark}[{inbound.key}] for {account_email}"
                                    )
                                else:
                                    logger.warn(
                                        f"Could not reset traffic in target inbound {inbound.remark}[{inbound.key}] for {account_email}"
                                    )
                        else:
                            logger.warn(
                                f"We could not found Account with email {account_email}"
                            )

                # if db_accounts_used_traffic and len(db_accounts_used_traffic) > 0:
                #     create_bulk_account_used_traffic(
                #         db=db, accounts_used_traffic=db_accounts_used_traffic
                #     )
                #     xui.api.reset_clients_traffic(inbound_id=inbound.key)
                #
                #     logger.info(
                #         f"Successfully saved all account used traffics with size {len(db_accounts_used_traffic)} for "
                #         f"inbound {inbound.remark} with key {inbound.key}"
                #     )
                # else:
                #     logger.warn(
                #         f"No client state in inbound {inbound.remark} with key {inbound.key} on {host.name}"
                #     )
            except Exception as error:
                # traceback.print_exception(error)
                logger.error(error)
                logger.error(
                    f"Could not sync traffics in host {host.name} and inbound {inbound.remark} with key {inbound.key}"
                )
                continue

        # for db_account in get_accounts(db=db, return_with_count=False):
        #     try:
        #         logger.debug(f"Account uuid: {db_account.uuid}")
        #         logger.debug(f"Account email: {db_account.email}")
        #         logger.debug(f"Account Expire time: {db_account.expired_at}")
        #         logger.debug(f"Account Status: {db_account.enable}")
        #
        #         if not db_account.enable:
        #             logger.debug("Account is disable, skipped to update traffic!")
        #             continue
        #
        #         account_sum_used_traffic = get_account_used_traffic(
        #             db=db, db_account=db_account, delta=0
        #         )
        #
        #         if account_sum_used_traffic:
        #             used_traffic = (
        #                 account_sum_used_traffic.upload
        #                 + account_sum_used_traffic.download
        #             )
        #
        #             update_account_used_traffic(
        #                 db=db, db_account=db_account, used_traffic=used_traffic
        #             )
        #     except Exception as error:
        #         logger.error(error)
        #         logger.error(f"Could not sync traffics for account {db_account.email} ")
        #         continue

        end = datetime.utcnow().timestamp()
        logger.info(
            f"End syncing accounts traffic from all inbounds in {int(end - start)} Sec"
        )


def review_accounts():
    now = datetime.utcnow().timestamp()
    logger.info("Start Review Accounts")

    with GetDB() as db:
        for account in get_accounts(db=db, return_with_count=False):
            account_expire_time = 0
            if account.expired_at:
                account_expire_time = account.expired_at.timestamp()

            # telegram_user_name = (
            #     account.user.telegram_username if account.user.telegram_username else ""
            # )

            if (0 < account_expire_time <= now) and account.enable:
                logger.info("Account has been expired due to expired time.")
                logger.info(f"Account uuid: {account.uuid}")
                logger.info(f"Account email: {account.email}")
                logger.info(f"Account Expire time: {account.expired_at}")
                logger.info(f"Account status: {account.enable}")
                update_account_status(db=db, db_account=account, enable=False)

                _send_notification(
                    db=db,
                    db_user=account.user,
                    message=messages.USER_NOTIFICATION_ACCOUNT_EXPIRED.format(
                        id=account.email,
                        service_title=account.service_title,
                        due=captions.EXPIRE_TIME,
                    ),
                    type_=NotificationType.account,
                    send_to_admin=True,
                )

            elif account.used_traffic >= account.data_limit > 0 and account.enable:
                logger.info(
                    "Account has been expired due to exceeded Data limit usage."
                )
                logger.info(f"Account uuid: {account.uuid}")
                logger.info(f"Account email: {account.email}")
                logger.info(f"Account Expire time: {account.expired_at}")
                logger.info(f"Account status: {account.enable}")

                update_account_status(db=db, db_account=account, enable=False)

                _send_notification(
                    db=db,
                    db_user=account.user,
                    message=messages.USER_NOTIFICATION_ACCOUNT_EXPIRED.format(
                        id=account.email,
                        service_title=account.service_title,
                        due=captions.EXCEEDED_DATA_LIMIT,
                    ),
                    type_=NotificationType.account,
                    send_to_admin=True,
                )
    logger.info("End Review Accounts")


def sync_accounts_status():
    now = datetime.utcnow().timestamp()
    logger.info("Start Sync accounts status " + str(datetime.now()))

    with GetDB() as db:
        for account in get_accounts(db=db, return_with_count=False):
            second_ago_updated = 0
            if account.modified_at:
                second_ago_updated = now - account.modified_at.timestamp()

            if second_ago_updated < config.REVIEW_ACCOUNTS_INTERVAL * 2:
                logger.info(f"Account uuid: {account.uuid}")
                logger.info(f"Account email: {account.email}")
                logger.info(f"Account expire time: {account.expired_at}")
                logger.info(f"Account status: {account.enable}")
                logger.info((f"Account modified at: {account.modified_at}"))
                if account.enable:
                    update_client_in_all_inbounds(
                        db=db, db_account=account, enable=True
                    )
                    logger.info(
                        f"Account with email {account.email} enable successfully"
                    )

                else:
                    update_client_in_all_inbounds(
                        db=db, db_account=account, enable=False
                    )
                    logger.info(
                        f"Account with email {account.email} disable successfully"
                    )
            else:
                logger.debug(f"Skip Account with email {account.email}")


def remove_disabled_accounts(last_days: int):
    today = datetime.now()
    last_day_later = today - timedelta(days=last_days)

    logger.info(
        f"Remove accounts that disabled before last {last_days} days/ {last_day_later}"
    )

    with GetDB() as db:
        for db_account in get_accounts(
            db=db, return_with_count=False, filter_enable=True, enable=False
        ):
            if (
                db_account.modified_at and db_account.modified_at < last_day_later
            ) or db_account.email.startswith(config.TEST_ACCOUNT_EMAIL_PREFIX):
                logger.info(
                    f"Try to delete account for {db_account.user.full_name} with modified date {db_account.modified_at}"
                    f" and email {db_account.email} and status {db_account.enable}"
                )
                delete_account(db=db, db_account=db_account)


def delete_account(db, db_account: Account):
    try:
        # delete_client_in_all_inbounds(db=db, db_account=db_account)

        remove_account(db=db, db_account=db_account)

    except Exception:
        logger.error("Error in delete this account")


def remove_unused_test_accounts(last_days: int):
    today = datetime.now()
    last_day_later = today - timedelta(days=last_days)

    logger.info(
        f"Remove Test accounts that Not used and created before last {last_days} days/ {last_day_later}"
    )

    with GetDB() as db:
        for db_account in get_accounts(
            db=db, return_with_count=False, filter_enable=True, test_account=True
        ):
            if (
                db_account.modified_at
                and db_account.modified_at < last_day_later
                and db_account.used_traffic == 0
                and db_account.email.startswith(config.TEST_ACCOUNT_EMAIL_PREFIX)
            ):
                logger.info(
                    f"Try to delete Test account for {db_account.user.full_name} with modified date {db_account.modified_at}"
                    f" and email {db_account.email} and status {db_account.enable}"
                )
                delete_account(db=db, db_account=db_account)


def _send_notification(
    db,
    db_user: User,
    message: str,
    type_: NotificationType,
    level: int = 0,
    send_to_admin: bool = False,
):
    create_notification(
        db=db,
        db_user=db_user,
        notification=NotificationCreate(
            user_id=db_user.id,
            approve=True,
            message=message,
            level=level,
            type=type_,
            send_to_admin=send_to_admin,
        ),
    )


def run_review_account_jobs():
    logger.info(f"Start Review Account Jobs")
    review_accounts()
    clean_up_inbounds()
    # sync_accounts_status()
    logger.info(f"End Review Account Jobs")


def run_remove_disabled_accounts_jobs():
    remove_disabled_accounts(config.REMOVE_DISABLED_ACCOUNTS_LAST_DAYS)
    remove_unused_test_accounts(config.REMOVE_UNUSED_TEST_ACCOUNTS_LAST_DAYS)


if config.ENABLE_SYNC_ACCOUNTS:
    scheduler.add_job(
        func=run_review_account_jobs,
        max_instances=1,
        trigger="interval",
        seconds=config.REVIEW_ACCOUNTS_INTERVAL,
    )

    scheduler.add_job(
        func=sync_new_accounts,
        max_instances=1,
        trigger="interval",
        seconds=config.SYNC_ACCOUNTS_INTERVAL,
    )

    scheduler.add_job(
        func=sync_accounts_traffic,
        max_instances=1,
        trigger="interval",
        seconds=config.SYNC_ACCOUNTS_TRAFFIC_INTERVAL,
    )
else:
    logger.warn("Sync accounts JOBS are disabled!")

if config.ENABLE_REMOVE_DISABLED_ACCOUNTS:
    scheduler.add_job(
        func=run_remove_disabled_accounts_jobs,
        max_instances=1,
        trigger="interval",
        seconds=config.REMOVE_DISABLED_ACCOUNTS_JOB_INTERVAL,
    )
else:
    logger.warn("Remove disabled account JOBS are disabled!")
