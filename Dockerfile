FROM python:3.13-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir flask requests

EXPOSE 8000
CMD ["python", "app.py"]

