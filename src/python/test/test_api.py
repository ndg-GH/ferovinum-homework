from pytest import fixture as _fixture
from requests import Session as _Session

from ferovinum import config as _config


class _ApiClient:

    def __init__(self):
        self.__url_start = f'http://{_config["WebServerHost"]}:{_config["WebServerPort"]}'
        self.__session = _Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get(self, path, params=None, status_code=None):
        return self.__get_checked_response(self.__session.get(self.__url_start + path, params=params), status_code)

    def post(self, path, json=None, status_code=None):
        return self.__get_checked_response(self.__session.post(self.__url_start + path, json=json), status_code)

    def close(self):
        self.__session.close()

    @staticmethod
    def __get_checked_response(response, status_code):
        if status_code is not None:
            assert (response.status_code in status_code if isinstance(status_code, (list, tuple, set)) else response.status_code == status_code)
        return response.json()


@_fixture(scope='module')
def api_client():
    api_client = _ApiClient()
    yield api_client
    api_client.close()


def test_get_client_balance(api_client):
    assert api_client.get('/balance/client/C-1') == [{'clientId': 'C-1', 'productId': 'P-1', 'quantity': 850},
                                                     {'clientId': 'C-1', 'productId': 'P-2', 'quantity': 1}]
    assert api_client.get('/balance/client/C-1?date=2020-01-15') == [{'clientId': 'C-1', 'productId': 'P-1', 'quantity': 950},
                                                                     {'clientId': 'C-1', 'productId': 'P-2', 'quantity': 500}]


def test_get_product_balance(api_client):
    assert api_client.get('/balance/product/P-1') == [{'clientId': 'C-1', 'productId': 'P-1', 'quantity': 850},
                                                      {'clientId': 'C-3', 'productId': 'P-1', 'quantity': 0}]
    assert api_client.get('/balance/product/P-1?date=2021-07-01') == [{'clientId': 'C-1', 'productId': 'P-1', 'quantity': 850},
                                                                      {'clientId': 'C-3', 'productId': 'P-1', 'quantity': 4999}]


def test_get_client_portfolio_metrics(api_client):
    assert api_client.get('/portfolio/client/C-1?date=2024-01-01') == {'lifeToDateFeeNotional': 13339.69,
                                                                       'lifeToDateProductNotional': 659900,
                                                                       'outstandingFeeNotional': 154573.73,
                                                                       'outstandingProductNotional': 40751.18,
                                                                       'weightedAverageRealisedAnnualisedYield': 11416.76,
                                                                       'weightedAverageRealisedDuration': 327.30}


def test_get_client_transactions(api_client):
    assert api_client.get('/transactions/client/C-1') == [{'clientId': 'C-1', 'productId': 'P-1', 'orderType': 'buy',
                                                           'price': 47.9, 'quantity': 1000, 'timestamp': '2020-01-01T10:00:00Z'},
                                                          {'clientId': 'C-1', 'productId': 'P-2', 'orderType': 'buy',
                                                           'price': 36.18, 'quantity': 500, 'timestamp': '2020-01-01T10:00:00Z'},
                                                          {'clientId': 'C-1', 'productId': 'P-1', 'orderType': 'sell',
                                                           'price': 49.46, 'quantity': 50, 'timestamp': '2020-01-01T11:00:00Z'},
                                                          {'clientId': 'C-1', 'productId': 'P-1', 'orderType': 'sell',
                                                           'price': 51.06, 'quantity': 100, 'timestamp': '2020-02-01T10:00:00Z'},
                                                          {'clientId': 'C-1', 'productId': 'P-2', 'orderType': 'sell',
                                                           'price': 43.83, 'quantity': 250, 'timestamp': '2020-06-15T10:00:00Z'},
                                                          {'clientId': 'C-1', 'productId': 'P-2', 'orderType': 'sell',
                                                           'price': 80.49, 'quantity': 249, 'timestamp': '2022-01-01T10:00:00Z'}]
    assert api_client.get('/transactions/client/C-3?fromDate=2021-01-01&toDate=2023-01-01') == [{'clientId': 'C-3', 'productId': 'P-1', 'orderType': 'sell',
                                                                                                 'price': 57.23, 'quantity': 1, 'timestamp': '2021-07-01T10:00:00Z'},
                                                                                                {'clientId': 'C-3', 'productId': 'P-1', 'orderType': 'sell',
                                                                                                 'price': 83.54, 'quantity': 4999, 'timestamp': '2022-12-01T10:00:00Z'}]


def test_get_product_transactions(api_client):
    assert api_client.get('/transactions/product/P-1') == [{'clientId': 'C-1', 'productId': 'P-1', 'orderType': 'buy',
                                                            'price': 47.9, 'quantity': 1000, 'timestamp': '2020-01-01T10:00:00Z'},
                                                           {'clientId': 'C-1', 'productId': 'P-1', 'orderType': 'sell',
                                                            'price': 49.46, 'quantity': 50, 'timestamp': '2020-01-01T11:00:00Z'},
                                                           {'clientId': 'C-1', 'productId': 'P-1', 'orderType': 'sell',
                                                            'price': 51.06, 'quantity': 100, 'timestamp': '2020-02-01T10:00:00Z'},
                                                           {'clientId': 'C-3', 'productId': 'P-1', 'orderType': 'buy',
                                                            'price': 47.9, 'quantity': 5000, 'timestamp': '2020-12-01T10:00:00Z'},
                                                           {'clientId': 'C-3', 'productId': 'P-1', 'orderType': 'sell',
                                                            'price': 57.23, 'quantity': 1, 'timestamp': '2021-07-01T10:00:00Z'},
                                                           {'clientId': 'C-3', 'productId': 'P-1', 'orderType': 'sell',
                                                            'price': 83.54, 'quantity': 4999, 'timestamp': '2022-12-01T10:00:00Z'}]
    assert api_client.get('/transactions/product/P-2?fromDate=2021-01-01&toDate=2023-01-01') == [{'clientId': 'C-1', 'productId': 'P-2', 'orderType': 'sell',
                                                                                                  'price': 80.49, 'quantity': 249, 'timestamp': '2022-01-01T10:00:00Z'}]
