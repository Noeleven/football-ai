FROM python:3.11-slim

WORKDIR /app

COPY collector_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY collector_service/ .

CMD ["python", "src/main.py"]