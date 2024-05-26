FROM python:3.12-alpine
WORKDIR /django-sqlite
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tests tests
COPY src src
CMD pytest -q --tb=no $TARGET