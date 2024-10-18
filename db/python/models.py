from sqlalchemy.sql.functions import now
from connection import Base
from sqlalchemy import Column, String, DECIMAL, ForeignKey, Boolean, Date, DateTime
from sqlalchemy.orm import relationship, column_property


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    full_name = column_property(first_name + " " + last_name)
    nickname = Column(String)
    email = Column(String)
    phone = Column(String)
    password = Column(String)
    role = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    operations = relationship('Operation', back_populates='operator')
    bids = relationship('Bid', back_populates='investor')


class Operation(Base):
    __tablename__ = 'operations'

    id = Column(String, primary_key=True)
    operator_id = Column(String, ForeignKey('users.id'))
    required_amount = Column(DECIMAL(15, 2), nullable=False)
    annual_interest = Column(DECIMAL(5, 2), nullable=False)
    deadline = Column(Date, nullable=False)
    current_amount = Column(DECIMAL(15, 2), default=0)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now())
    operator = relationship('User', back_populates='operations')
    bids = relationship('Bid', back_populates='operation')


class Bid(Base):
    __tablename__ = 'bids'

    id = Column(String, primary_key=True)
    investor_id = Column(String, ForeignKey('users.id'))
    operation_id = Column(String, ForeignKey('operations.id'))
    invested_amount = Column(DECIMAL(15, 2), nullable=False)
    interest_rate = Column(DECIMAL(5, 2), nullable=False)
    bid_date = Column(DateTime, default=now())
    investor = relationship('User', back_populates='bids')
    operation = relationship('Operation', back_populates='bids')
