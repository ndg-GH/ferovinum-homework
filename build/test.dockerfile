FROM ferovinum-web:latest

RUN set -ex \
    && /ferovinum/venv/bin/python -m pip install pytest requests

COPY --chown=ferovinum ./src/python/test /ferovinum/src/python/test

CMD TEST_TIMESTAMP=$(date +"%Y%m%d_%H%M%S_%N") bash -c '/ferovinum/venv/bin/pytest /ferovinum/src/python/test 1>/ferovinum/test_output/pytest-$TEST_TIMESTAMP-out.log 2>/ferovinum/test_output/pytest-$TEST_TIMESTAMP-err.log'
