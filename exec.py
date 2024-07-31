#!/usr/bin/env python3

from json import dump
from os import environ
from pathlib import Path
from subprocess import check_call
from sys import argv


config = {'LoggingLevel': 'DEBUG',
          'PostgresHost': 'db',
          'PostgresPort': 5432,
          'PostgresSuperUserName': 'postgres',
          'PostgresSuperUserPassword': 'p@ssword!',
          'PostgresDatabaseName': 'ferovinum_db',
          'WebServerHost': 'web',
          'WebServerPort': 8080}

root_dir_path = Path(__file__).parent
build_dir_path = root_dir_path / 'build'
package_dir_path = root_dir_path / 'src' / 'python' / 'package'
project_name = 'ferovinum'


def run_docker_compose(*args):
    check_call(('docker', 'compose', '-p', project_name) + args,
               cwd=build_dir_path,
               env=dict(environ,
                        POSTGRES_PASSWORD=config['PostgresSuperUserPassword'],
                        FEROVINUM_ROOT_DIR=str(root_dir_path)))


def build():
    with open(package_dir_path / 'ferovinum' / '__config__.json', mode='w') as file:
        dump(config, file, indent=4)
    for service_name in ('db', 'web', 'db-init', 'test'):
        run_docker_compose('build', service_name)


def start():
    run_docker_compose('up', '-d', 'web', 'db-init', 'db')


def stop():
    run_docker_compose('down')


def test():
    run_docker_compose('up', 'test')


def run_all():
    stop()
    build()
    start()


def main(cmd, *args):
    cmd_func = {'all': run_all,
                'build': build,
                'start': start,
                'stop': stop,
                'test': test,
                'docker': run_docker_compose}.get(cmd)
    if cmd_func is None:
        raise Exception('unknown command', cmd, args)
    cmd_func(*args)


if __name__ == '__main__':
    main(*argv[1:])
