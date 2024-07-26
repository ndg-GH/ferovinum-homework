from json import load as _load
from logging import getLogger as _getLogger, Formatter as _Formatter, StreamHandler as _StreamHandler
from pathlib import Path as _Path
from sys import stdout as _stdout


def _get_config():
    with open(_Path(__file__).parent / '__config__.json', mode='r') as file:
        return _load(file)


def _get_logger():
    handler = _StreamHandler(_stdout)
    handler.setLevel(config['LoggingLevel'])
    handler.setFormatter(_Formatter('[%(asctime)s][%(levelname)s]%(message)s'))
    root = _getLogger()
    root.setLevel(config['LoggingLevel'])
    root.addHandler(handler)
    return _getLogger(__name__)


config = _get_config()
logger = _get_logger()
