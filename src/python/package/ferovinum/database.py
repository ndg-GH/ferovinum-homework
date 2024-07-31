from datetime import date as _date, datetime as _datetime
from decimal import Decimal as _Decimal

from sqlalchemy import URL as _URL, UniqueConstraint as _UniqueConstraint
from sqlmodel import Field as _Field, Index as _Index, SQLModel as _SQLModel, create_engine as _create_engine, \
                     Session as _Session, select as _select

from . import config as _config


def _get_price_factor(t0, t1, fee):
    months = 12 * (t1.year - t0.year) + t1.month - t0.month
    if (t1.day, t1.hour, t1.minute, t1.second) >= (t0.day, t0.hour, t0.minute, t0.second):
        months += 1
    return (1 + fee / 12) ** months


class Client(_SQLModel, table=True):
    id: str = _Field(max_length=20, primary_key=True)
    fee: _Decimal = _Field(max_digits=10, decimal_places=4, nullable=False)


class Product(_SQLModel, table=True):
    id: str = _Field(max_length=20, primary_key=True)
    price: _Decimal = _Field(max_digits=10, decimal_places=2, nullable=False)


class Stock(_SQLModel, table=True):
    id: int = _Field(primary_key=True)
    client_id: str = _Field(foreign_key='client.id')
    product_id: str = _Field(foreign_key='product.id')
    timestamp: _datetime = _Field(nullable=False, index=True)
    quantity: int = _Field(nullable=False)

    __table_args__ = (_Index('idx_stock_client_product_timestamp', 'client_id', 'product_id', 'timestamp'),)


class Balance(_SQLModel, table=True):
    id: int = _Field(primary_key=True)
    date: _date = _Field(nullable=False)
    client_id: str = _Field(foreign_key='client.id')
    product_id: str = _Field(foreign_key='product.id')
    quantity: int = _Field(nullable=False)

    __table_args__ = (_UniqueConstraint('date', 'client_id', 'product_id'),)


class Transaction(_SQLModel, table=True):
    id: int = _Field(primary_key=True)
    client_id: str = _Field(foreign_key='client.id')
    product_id: str = _Field(foreign_key='product.id')
    timestamp: _datetime = _Field(nullable=False, index=True)
    price: _Decimal = _Field(max_digits=10, decimal_places=2, nullable=False)
    quantity: int = _Field(nullable=False)

    __table_args__ = (_Index('idx_transaction_client_timestamp', 'client_id', 'product_id', 'timestamp'),)


def create_order(client_id, product_id, timestamp, type_, quantity):
    is_buy = True if type_ == 'buy' else False if type_ == 'sell' else None
    if is_buy is None:
        raise Exception('WrongOrderType', type_)
    if quantity <= 0:
        raise Exception('WrongOrderQuantity', quantity)
    with _Session(engine) as session:
        client_fee = session.exec(_select(Client).where(Client.id == client_id)).one().fee
        product_price = session.exec(_select(Product).where(Product.id == product_id)).one().price
        if is_buy:
            session.add(Stock(client_id=client_id, product_id=product_id, timestamp=timestamp, quantity=quantity))
            session.add(Transaction(client_id=client_id, product_id=product_id, timestamp=timestamp,
                                    price=product_price, quantity=quantity))
        else:
            qty_to_sell = quantity
            for stock in session.exec(_select(Stock).where(Stock.client_id == client_id,
                                                           Stock.product_id == product_id,
                                                           Stock.timestamp <= timestamp).order_by('timestamp')):
                transaction_qty = min(qty_to_sell, stock.quantity)
                sell_price = product_price * _get_price_factor(stock.timestamp, timestamp, client_fee)
                session.add(Transaction(client_id=client_id, product_id=product_id, timestamp=timestamp,
                                        price=sell_price, quantity=-transaction_qty))
                if stock.quantity <= qty_to_sell:
                    session.delete(stock)
                else:
                    stock.quantity -= qty_to_sell
                    session.add(stock)
                qty_to_sell -= transaction_qty
                if qty_to_sell <= 0:
                    break
            else:
                raise Exception('SellQuantityTooHigh', client_id, product_id, quantity)
        timestamp_date = timestamp.date()
        balance = session.exec(_select(Balance).where(Balance.client_id == client_id,
                                                      Balance.product_id == product_id).order_by(Balance.date.desc())).first()
        if balance is None or balance.date != timestamp_date:
            balance = Balance(date=timestamp_date, client_id=client_id, product_id=product_id, quantity=balance.quantity if balance is not None else 0)
        balance.quantity += quantity if is_buy else -quantity
        session.add(balance)
        session.commit()


engine = _create_engine(_URL.create('postgresql+psycopg2',
                                    username=_config['PostgresSuperUserName'],
                                    password=_config['PostgresSuperUserPassword'],
                                    host=_config['PostgresHost'],
                                    database=_config['PostgresDatabaseName']))
