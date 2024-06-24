from sqlalchemy import Enum, Column, ForeignKey, Integer, String, DateTime, Float, Boolean, Table, TIMESTAMP
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from schemas.user import UserRoles
from db.database import Base


class ModelBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


organization_category_table = Table(
    "organization_category_table",
    Base.metadata,
    Column("left_id", ForeignKey("organizations.id"), primary_key=True),
    Column("right_id", ForeignKey("categories.id"), primary_key=True),
)


class City(ModelBase):
    __tablename__ = "cities"

    name = Column(String)
    organizations = relationship("Organization", back_populates="city", order_by='desc(Organization.name)',
                                 lazy='dynamic',
                                 cascade="all, delete-orphan")

    income = Column(Integer, default=0)
    incomeMonth = Column(Integer, default=0)

    owner_id = Column(Integer, ForeignKey("users.id", name="fk_owner"))
    owner = relationship("User", foreign_keys=[owner_id], backref="cities")


class Category(ModelBase):
    __tablename__ = "categories"

    name = Column(String)
    organizations = relationship(
        "Organization", secondary=organization_category_table, back_populates="categories"
    )


class Image(ModelBase):
    __tablename__ = "images"

    name = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))


class Organization(ModelBase):
    __tablename__ = "organizations"

    name = Column(String)
    images = relationship("Image", cascade="all, delete-orphan")

    categories = relationship(
        "Category", secondary=organization_category_table, back_populates="organizations"
    )

    site = Column(String, nullable=True)
    description = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    address = Column(String, nullable=False)
    workingDay = Column(String, nullable=False)

    paidFor = Column(Boolean, default=False)
    hidden = Column(Boolean, default=True)

    statAll = Column(Integer, default=0)
    statDay = Column(Integer, default=0)

    city_id = Column(Integer, ForeignKey("cities.id"))
    city = relationship("City", back_populates="organizations")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="organizations")

    next_pay_time = Column(DateTime, default=None, nullable=True)


class User(ModelBase):
    __tablename__ = "users"

    role = Column(Enum(UserRoles), default=UserRoles.COMMON)
    rubles = Column(Integer, default=0, nullable=False)
    organizations = relationship("Organization", back_populates="owner", cascade="all, delete",
                                 passive_deletes=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    city = relationship("City", foreign_keys=[city_id], backref="users")

