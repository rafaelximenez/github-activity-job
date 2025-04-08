FROM python:3.9-slim-buster

WORKDIR /app

COPY main.py /app

RUN pip install --no-cache-dir requests

CMD ["python", "main.py"]