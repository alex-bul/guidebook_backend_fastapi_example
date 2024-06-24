import csv
import datetime

from core.utils import ADMINS

from db.database import SessionLocal
from db.models import Organization as OrganizationModel
from db.methods import get_category_by_name, create_category, get_city, create_city, get_organization, get_user, \
    create_user

from schemas.user import CreateUser
from schemas.category import Category, CreateCategory
from schemas.city import CreateCity

SOURCE_FILE = 'data.csv'


def admins_and_city_create():
    db = SessionLocal()
    for user_id in ADMINS:
        if not get_user(db, user_id):
            create_user(db, CreateUser(id=user_id, role=10))

    main_city = get_city(db, 1)
    if not main_city:
        create_city(db, CreateCity(name="Алексин"))


def upload_data_from_source():
    with open(SOURCE_FILE, newline='\n', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';', quotechar='"')
        reader.__next__()
        db = SessionLocal()

        main_city = get_city(db, 1)
        if not main_city:
            create_city(db, CreateCity(name="Алексин"))

        for row in reader:
            organization_id, name, category_data, site, email, address, lat, \
            lng, phone, tpe, workingDay, description = row[:-3]

            if get_organization(db, organization_id):
                continue

            category_list = []

            category_name_list = list(set([name.strip() for name in category_data.strip(';').split(';')]))

            for category_name in category_name_list:
                category_object = get_category_by_name(db, category_name)
                if not category_object:
                    category_object = create_category(db, CreateCategory(name=category_name))
                category_list.append(category_object)
            db_unit = OrganizationModel(
                id=organization_id,
                name=name,
                site=site,
                description=description,
                email=email,
                phone=phone,
                address=address,
                workingDay=workingDay,
                hidden=False,
                next_pay_time=datetime.datetime(year=3000, month=1, day=1, hour=1, minute=1, second=1),

                categories=category_list,
                city_id=1)
            db.add(db_unit)
            db.commit()
            db.refresh(db_unit)

            print(f"Добавил в базу #{organization_id}")
