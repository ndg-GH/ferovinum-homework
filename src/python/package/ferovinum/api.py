from datetime import date as _date, datetime as _datetime, timedelta as _timedelta, timezone as _timezone

from fastapi import FastAPI as _FastAPI, Path as _Path, Query as _Query
from pydantic import BaseModel as _BaseModel
from sqlalchemy import func as _func
from sqlmodel import Session as _Session, select as _select

from . import config as _config
from .database import Transaction as _Transaction, create_order as _create_order, engine as _engine


class Config:
    bind = f'0.0.0.0:{_config["WebServerPort"]}'


class _OrderRequest(_BaseModel):
    clientId: str
    productId: str
    type: str
    quantity: int


app = _FastAPI()



def _get_transactions(query, from_date, to_date):
    with _Session(_engine) as session:
        if from_date is not None:
            query = query.where(_Transaction.timestamp >= from_date)
        if to_date is not None:
            query = query.where(_Transaction.timestamp <= to_date)
        return [{'clientId': x.client_id, 'productId': x.product_id, 'orderType': 'buy' if x.quantity > 0 else 'sell',
                 'price': x.price, 'quantity': abs(x.quantity), 'timestamp': x.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')}
                for x in session.exec(query).all()]


@app.post('/order')
def create_order(order_request: _OrderRequest):
    return _create_order(order_request.clientId, order_request.productId, _datetime.now(tz=_timezone.utc),
                         order_request.type, order_request.quantity)


@app.get('/balance/client/{clientId}')
def get_client_balance(client_id: str = _Path(alias='clientId'),
                       date: _date | None = _Query(None)):
    """Returns a list of all product quantities for given clientId.
       The optional date parameter specifies a particular date to extract a snapshot past result,
           otherwise the latest result will be returned."""
    with _Session(_engine) as session:
        query = session.query(_Transaction.product_id, _func.sum(_Transaction.quantity).label('quantity')) \
                       .filter(_Transaction.client_id == client_id)
        if date is not None:
            query = query.filter(_Transaction.timestamp < date+ _timedelta(days=1))
        return [{'clientId': client_id, 'productId': x.product_id, 'quantity': x.quantity}
                for x in query.group_by(_Transaction.product_id).all()]


@app.get('/balance/product/{productId}')
def get_product_balance(product_id: str = _Path(alias='productId'),
                        date: _date | None = _Query(None)):
    """Returns a list of all product quantities for given productId.
       The optional date parameter specifies a particular date to extract a snapshot past result,
           otherwise the latest result will be returned."""
    with _Session(_engine) as session:
        query = session.query(_Transaction.client_id, _func.sum(_Transaction.quantity).label('quantity')) \
                       .filter(_Transaction.product_id == product_id)
        if date is not None:
            query = query.filter(_Transaction.timestamp < date + _timedelta(days=1))
        return [{'clientId': x.client_id, 'productId': product_id, 'quantity': x.quantity}
                for x in query.group_by(_Transaction.client_id).all()]


@app.get('/portfolio/client/{clientId}')
def get_client_portfolio_metrics(client_id: str = _Path(alias='clientId'),
                                 date: _date | None = _Query(None)):
    """Returns portfolio metrics for given clientId.
       The optional date parameter specifies a particular date to extract a snapshot past result,
           otherwise the latest result will be returned."""
    return {'lifeToDateFeeNotional': None,
            'lifeToDateProductNotional': None,
            'outstandingFeeNotional': None,
            'outstandingProductNotional': None,
            'weightedAverageRealisedAnnualisedYield': None,
            'weightedAverageRealisedDuration': None}


@app.get('/transactions/client/{clientId}')
def get_client_transactions(client_id: str = _Path(alias='clientId'),
                            from_date: _date | None = _Query(None, alias='fromDate'),
                            to_date: _date | None = _Query(None, alias='toDate')):
    """Returns a list of all transactions for given clientId.
       The optional fromDate and toDate parameters specify a particular date range to filter results,
           otherwise all transactions will be returned."""
    return _get_transactions(_select(_Transaction).where(_Transaction.client_id == client_id), from_date, to_date)


@app.get('/transactions/product/{productId}')
def get_product_transactions(product_id: str = _Path(alias='productId'),
                             from_date: _date | None = _Query(None, alias='fromDate'),
                             to_date: _date | None = _Query(None, alias='toDate')):
    """Returns a list of all transactions for given productId.
       The optional fromDate and toDate parameters specify a particular date range to filter results,
           otherwise all transactions will be returned."""
    return _get_transactions(_select(_Transaction).where(_Transaction.product_id == product_id), from_date, to_date)
