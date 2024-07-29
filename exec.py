#!/usr/bin/env python3

if __name__ != '__main__':
    raise Exception('this script is meant to be executed directly')

from json import dump
from os import environ
from pathlib import Path
from subprocess import check_call
from sys import argv, executable


config = {'ClientIdMaxLength': 120,
          'LoggingLevel': 'DEBUG',
          'PostgresHost': 'localhost',
          'PostgresPort': 60001,
          'PostgresSuperUserName': 'postgres',
          'PostgresSuperUserPassword': 'p@ssword!',
          'PostgresDatabaseName': 'ferovinum_db',
          'ProductIdMaxLength': 120,
          'WebServerPort': 8080}

root_dir_path = Path(__file__).parent
build_dir_path = root_dir_path / 'build'
python_dir_path = root_dir_path / 'src' / 'python'
project_name = 'ferovinum'


def run_docker_compose(*args):
    check_call(('docker', 'compose', '-p', project_name) + args,
               cwd=build_dir_path,
               env=dict(environ, POSTGRES_PASSWORD=config['PostgresSuperUserPassword']))


def build():
    with open(python_dir_path / 'ferovinum' / '__config__.json', mode='w') as file:
        dump(config, file)
    run_docker_compose('build')


def start():
    run_docker_compose('up', '-d')


def load():
    check_call((executable, str(python_dir_path / 'init_db.py')))


def stop():
    run_docker_compose('down')


def test():
    check_call(('pytest', 'test'), cwd=root_dir_path)


def run_all():
    stop()
    build()
    start()
    load()


cmd, *args = argv[1:]

if cmd == 'all':
    run_all(*args)
elif cmd == 'build':
    build(*args)
elif cmd == 'start':
    start(*args)
elif cmd == 'load':
    load(*args)
elif cmd == 'stop':
    stop(*args)
elif cmd == 'test':
    test(*args)
elif cmd == 'docker':
    run_docker_compose(*args)
else:
    raise Exception('unknown command', cmd, args)
