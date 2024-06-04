FROM python:3.8-slim-buster

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements/requirements.txt
EXPOSE 90

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "90"]