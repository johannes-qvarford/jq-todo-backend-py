FROM python:3.10

ARG ENV=dev
ENV POETRY_VERSION=1.1.13 ENV=${ENV}

WORKDIR /code

COPY wait-for-it.sh /code/

COPY poetry.lock pyproject.toml /code/

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN pip install "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false \
    && poetry install $(test "$ENV" == production && echo "--no-dev") --no-interaction --no-ansi

COPY ./jqtodobackend /code/jqtodobackend
CMD ["uvicorn", "jqtodobackend.backend:app", "--host", "0.0.0.0", "--port", "8080"]