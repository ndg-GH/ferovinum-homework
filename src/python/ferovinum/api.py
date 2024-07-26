from datetime import date as _date

from fastapi import FastAPI as _FastAPI, Path as _Path, Query as _Query

from . import config as _config, logger as _logger


class Config:
    bind = f'0.0.0.0:{_config["WebServerPort"]}'


app = _FastAPI()


@app.get('/balance/client/{clientId}')
def get_client_balance(clientId: str = _Path(max_length=_config['ClientIdMaxLength']),
                       date: _date | None = _Query(None)):
    """Returns a list of all product quantities for given clientId.
       The optional date parameter specifies a particular date to extract a snapshot past result,
           otherwise the latest result will be returned."""
    _logger.debug(f'get_client_balance - clientId is {clientId!r}, date is {date!r}')
    return []


@app.get('/balance/product/{productId}')
def get_product_balance(productId: str,
                        date: _date | None = _Query(None)):
    """Returns a list of all product quantities for given productId.
       The optional date parameter specifies a particular date to extract a snapshot past result,
           otherwise the latest result will be returned."""
    _logger.debug(f'get_product_balance - productId is {productId!r}, date is {date!r}')
    return []


@app.get('/portfolio/client/{clientId}')
def get_client_portfolio_metrics(clientId: str = _Path(max_length=_config['ClientIdMaxLength']),
                                 date: _date | None = _Query(None)):
    """Returns portfolio metrics for given clientId.
       The optional date parameter specifies a particular date to extract a snapshot past result,
           otherwise the latest result will be returned."""
    _logger.debug(f'get_client_portfolio_metrics - clientId is {clientId!r}, date is {date!r}')
    return {'lifeToDateFeeNotional': None,
            'lifeToDateProductNotional': None,
            'outstandingFeeNotional': None,
            'outstandingProductNotional': None,
            'weightedAverageRealisedAnnualisedYield': None,
            'weightedAverageRealisedDuration': None}


@app.get('/transactions/client/{clientId}')
def get_client_transactions(clientId: str = _Path(max_length=_config['ClientIdMaxLength']),
                            fromDate: _date | None = _Query(None),
                            toDate: _date | None = _Query(None)):
    """Returns a list of all transactions for given clientId.
       The optional fromDate and toDate parameters specify a particular date range to filter results,
           otherwise all transactions will be returned."""
    _logger.debug(f'get_client_transactions - clientId is {clientId!r}, fromDate is {fromDate!r}, fromDate is {toDate!r}')
    return []


@app.get('/transactions/product/{productId}')
def get_product_transactions(productId: str = _Path(max_length=_config['ProductIdMaxLength']),
                             fromDate: _date | None = _Query(None),
                             toDate: _date | None = _Query(None)):
    """Returns a list of all transactions for given productId.
       The optional fromDate and toDate parameters specify a particular date range to filter results,
           otherwise all transactions will be returned."""
    _logger.debug(f'get_product_transactions - productId is {productId!r}, fromDate is {fromDate!r}, fromDate is {toDate!r}')
    return []

