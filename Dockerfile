FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ARG PIP_TRUSTED_HOST=mirrors.aliyun.com
ARG PIP_DEFAULT_TIMEOUT=120
ARG PIP_RETRIES=5

ENV PIP_INDEX_URL=${PIP_INDEX_URL}
ENV PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}

WORKDIR /app

COPY requirements-backend.txt /app/requirements-backend.txt
RUN pip install \
    --no-cache-dir \
    --retries ${PIP_RETRIES} \
    --default-timeout ${PIP_DEFAULT_TIMEOUT} \
    -r /app/requirements-backend.txt

COPY . /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend_mvp.app:app", "--host", "0.0.0.0", "--port", "8000"]
