ARG PYTHON_VER

FROM python:${PYTHON_VER:?} AS python-base


FROM python-base AS poetry
RUN pip install poetry
WORKDIR /workspace
COPY pyproject.toml poetry.lock /workspace/


FROM poetry AS test-base
ARG PYDANTIC_SETTINGS_VER

# We need to run tests as a non-root user, otherwise file permissions are ignored
RUN useradd python && mkdir /home/python && chown python /home/python
USER python

RUN poetry install --with test \
    && poetry run pip install --force-reinstall "pydantic-settings${PYDANTIC_SETTINGS_VER}"


FROM test-base AS test
RUN --mount=source=.,target=/workspace,rw \
    --mount=type=cache,uid=1000,target=.pytest_cache \
    poetry run pytest


FROM poetry AS lint
RUN poetry install --with lint


FROM lint AS lint-flake8
RUN --mount=source=.,target=/workspace,rw \
    poetry run flake8


FROM lint AS lint-black
RUN --mount=source=.,target=/workspace,rw \
    poetry run black --check --diff .


FROM lint AS lint-isort
RUN --mount=source=.,target=/workspace,rw \
    poetry run isort --check --diff .


FROM lint AS lint-mypy
RUN --mount=source=.,target=/workspace,rw \
    --mount=type=cache,target=.mypy_cache \
    poetry run mypy .


FROM poetry AS build-example
RUN --mount=source=.,target=.,rw \
    mkdir -p /wheels \
    && poetry build \
    && cp dist/pydantic_settings_file_envar-*.whl /wheels \
    && cd example \
    && poetry build \
    && mkdir -p /wheels && cp dist/*.whl /wheels/
RUN ls /wheels


FROM python-base AS example
RUN --mount=from=build-example,source=/wheels,target=/wheels \
    pip install --no-cache-dir /wheels/*.whl
ENTRYPOINT ["file-envar-example"]


FROM example AS test-example
SHELL ["bash", "-xeuo", "pipefail", "-c"]
RUN echo -n 'secret123' > /tmp/secret
RUN THRESHOLD=9000 LAUNCH_CODE_FILE=/tmp/secret file-envar-example > /tmp/out
RUN diff -u /tmp/out <(echo "Loaded settings: threshold=9000 launch_code='secret123'")
