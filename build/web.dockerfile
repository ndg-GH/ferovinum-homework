FROM python:3.12.4-slim

RUN mkdir -p /ferovinum/build && \
    mkdir /ferovinum/src && \
    mkdir /ferovinum/work && \
    addgroup ferovinum &&  \
    useradd -g ferovinum ferovinum

WORKDIR /ferovinum/work

COPY ./build/requirements.txt /ferovinum/build/requirements.txt

RUN set -ex \
    && python3 -m venv /ferovinum/venv \
    && /ferovinum/venv/bin/python -m pip install --upgrade pip setuptools wheel \
    && /ferovinum/venv/bin/python -m pip install --no-cache-dir -r /ferovinum/build/requirements.txt \
    && rm -rf /ferovinum/build

RUN chown -R ferovinum:ferovinum /ferovinum

COPY ./src/python/package/ferovinum /ferovinum/src/python/package/ferovinum

RUN chown -R ferovinum:ferovinum /ferovinum/src

USER ferovinum

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH "/ferovinum/src/python/package"

CMD /ferovinum/venv/bin/hypercorn --config python:ferovinum.api.Config ferovinum.api:app
