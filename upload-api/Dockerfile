FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY main.py .

ENV DATA_DIR=/data/uploads
EXPOSE 5000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=5000"]
