FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev mariadb-dev pkgconfig

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["daphne", "FD.asgi:application", "--bind", "0.0.0.0", "--port", "8000"]
