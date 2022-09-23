FROM python:3.10

RUN pip install "poetry==1.2.1"

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev --no-interaction --no-ansi

COPY . /code

ENTRYPOINT ["python"]
CMD ["app/gui.py" ]
