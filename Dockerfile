FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-backend.txt /app/requirements-backend.txt
RUN pip install --no-cache-dir -r /app/requirements-backend.txt

COPY . /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend_mvp.app:app", "--host", "0.0.0.0", "--port", "8000"]
