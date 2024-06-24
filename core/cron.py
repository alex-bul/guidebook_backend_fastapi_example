import logging
import random
import time

import pytz

from typing import List
from datetime import datetime
from db.database import SessionLocal
from db.models import Organization, City

from sqlalchemy.orm import Session
from vk_tools import send_payment_url


def delete_day_stat():
    db: Session = SessionLocal()
    db.query(Organization).update({"statDay": 0})
    db.commit()
    print("Удалил стату")

    # накрутка
    for organization in db.query(Organization).all():
        organization.statDay = random.randint(1, 150)
        # db.query(Organization).filter(Organization.id == organization.id).update({"statDay": random.randint(1, 300)})
    db.commit()
    db.close()
    print("Накрутил стату")


def check_payments_needs():
    db: Session = SessionLocal()
    organisations: List[Organization] = db.query(Organization).filter(Organization.hidden == False,
                                                                      Organization.next_pay_time <= datetime.now())
    for org in organisations:
        try:
            send_payment_url(org.owner_id, org.id, message=f"Оплатите продление подписки для «{org.name}»")
        except Exception as ex:
            print(ex)
        org.hidden = True
        db.commit()


def delete_month_income():
    db: Session = SessionLocal()
    db.query(City).update({"incomeMonth": 0})
    db.commit()
    print("Удалил месячный доход городов")


def wait_midnight_and_do_actions():
    current_time = datetime.now(pytz.timezone('Europe/Moscow'))
    while (current_time.hour, current_time.minute) != (0, 0):
        time.sleep(59)
        current_time = datetime.now(pytz.timezone('Europe/Moscow'))
    logging.info("doing midnight actions")
    delete_day_stat()
    check_payments_needs()


def wait_month_start_and_do_actions():
    current_time = datetime.now(pytz.timezone('Europe/Moscow'))
    while current_time.day != 1:
        time.sleep(60 * 60 * 1)
        current_time = datetime.now(pytz.timezone('Europe/Moscow'))
    logging.info("doing month_start actions")
    delete_month_income()
