FROM python:3.10-slim

WORKDIR /usr/src/flask_server

COPY . .

RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

ENV VIRTUAL_ENV=/usr/src/flask_server/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
