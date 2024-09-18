from sqlalchemy import ForeignKey, Column, Text, String, Boolean, Enum, Integer, BigInteger, DateTime, func, DATETIME
from database import *
import constants
from ulid import ULID


class Admin(Base):
    __tablename__ = 'Admin'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Chat_Id = Column(BigInteger, unique=True, nullable=False)
    SuperAdmin = Column(Boolean, nullable=False, default=False)


class Setting(Base):
    __tablename__ = 'Settings'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Enabled = Column(BigInteger, unique=False, nullable=False, default=True)


class MetaData(Base):
    __tablename__ = 'MetaData'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Channel_Id = Column(Text, nullable=False)
    Support_Id = Column(Text, nullable=False)
    Bot_Id = Column(Text, nullable=False)


class Servers(Base):
    __tablename__ = 'Servers'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Remark = Column(Text, nullable=False)
    Url = Column(Text, nullable=False)
    UserName = Column(Text, nullable=False)
    Password = Column(Text, nullable=False)
    OrderBy = Column(Integer, nullable=True)


class Inbounds(Base):
    __tablename__ = 'Inbounds'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Remark = Column(Text, nullable=False)
    Server_Id = Column(ForeignKey('Servers.Id', ondelete='CASCADE'), nullable=False)
    Address = Column(Text, nullable=False)
    Sni = Column(Text, nullable=False)
    Network = Column(Enum(constants.Network), nullable=False, default=constants.Network.tcp)
    Security = Column(Enum(constants.Security), nullable=False, default=constants.Security.none)
    HeaderType = Column(Enum(constants.HeaderType), nullable=False, default=constants.HeaderType.none)
    Panel_Inbound_Id = Column(Integer, nullable=False)
    Inbound_Port = Column(Integer, nullable=False)
    Limit = Column(Integer, nullable=False, default=250)
    OrderBy = Column(Integer, nullable=True)


class TestInbounds(Base):
    __tablename__ = 'TestInbounds'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Remark = Column(Text, nullable=False)
    Server_Id = Column(ForeignKey('Servers.Id', ondelete='CASCADE'), nullable=False)
    Address = Column(Text, nullable=False)
    Sni = Column(Text, nullable=False)
    Network = Column(Enum(constants.Network), nullable=False, default=constants.Network.tcp)
    Security = Column(Enum(constants.Security), nullable=False, default=constants.Security.none)
    HeaderType = Column(Enum(constants.HeaderType), nullable=False, default=constants.HeaderType.none)
    Panel_Inbound_Id = Column(Integer, nullable=False)
    Inbound_Port = Column(Integer, nullable=False)
    Limit = Column(Integer, nullable=False, default=250)
    OrderBy = Column(Integer, nullable=True)


class Subscriptions(Base):
    __tablename__ = 'Subscriptions'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Days = Column(Integer, nullable=False)
    Total_GB = Column(Integer, nullable=False)
    Number_Of_Users = Column(Integer, nullable=False)
    Price = Column(Integer, nullable=False)
    OrderBy = Column(Integer, nullable=True)


class Users(Base):
    __tablename__ = 'Users'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Chat_Id = Column(BigInteger, unique=True, nullable=False)
    TestAccount = Column(Boolean, nullable=False, default=False)
    Wallet = Column(BigInteger, nullable=False, default=0)


class UsersTasks(Base):
    __tablename__ = 'UsersTasks'
    Id = Column(String(26), primary_key=True, default=lambda: str(ULID()))
    User_Id = Column(ForeignKey('Users.Id', ondelete='CASCADE'), nullable=False)
    Message_Id = Column(BigInteger, nullable=False)
    ExpirationDate = Column(DateTime, nullable=False)


class UsersServices(Base):
    __tablename__ = 'UsersServices'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Inbound_Id = Column(ForeignKey('Inbounds.Id', ondelete='CASCADE'), nullable=True)
    Test_Inbound_Id = Column(ForeignKey('TestInbounds.Id', ondelete='CASCADE'), nullable=True)
    Subscription_Id = Column(ForeignKey('Subscriptions.Id', ondelete='CASCADE'), nullable=True)
    User_Id = Column(ForeignKey('Users.Id', ondelete='CASCADE'), nullable=False)
    Email = Column(Text, unique=True, nullable=False)
    UUID = Column(Text, unique=True, nullable=False)
    Days = Column(Integer, nullable=False)
    Number_Of_Users = Column(Integer, nullable=False)
    ExpirationDate = Column(DateTime, nullable=False)
    Total_GB = Column(BigInteger, nullable=False)
    Usage = Column(BigInteger, nullable=False, default=0)
    Remained = Column(BigInteger, nullable=False, default=0)


class Payments(Base):
    __tablename__ = 'Payments'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    User_Id = Column(ForeignKey('Users.Id', ondelete='CASCADE'), nullable=False)
    Payment_Id = Column(Text, nullable=False)
    Authority = Column(Text, nullable=False)
    Ref_Id = Column(Text, nullable=True)
    Amount = Column(BigInteger, nullable=False)
    Status = Column(Boolean, nullable=True, default=None)


class DiscountCodes(Base):
    __tablename__ = 'DiscountCodes'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Code = Column(Text, unique=True, nullable=False)
    Percent = Column(Integer, nullable=False, default=0)
