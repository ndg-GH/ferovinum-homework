FROM ferovinum-web:latest

RUN mkdir /ferovinum/data

COPY --chown=ferovinum ./data /ferovinum/data
COPY --chown=ferovinum ./src/python/script/init_db.py /ferovinum/src/python/script/init_db.py

CMD /ferovinum/venv/bin/python /ferovinum/src/python/script/init_db.py
