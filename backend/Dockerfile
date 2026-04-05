FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp/cache 

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-vie \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    sed \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir "numpy<2.0" && \
    pip install --no-cache-dir accelerate transformers sentence-transformers && \
    pip install --no-cache-dir -r requirements.txt

RUN sed -i '1i import torch.nn as nn' /usr/local/lib/python3.10/site-packages/transformers/integrations/accelerate.py

COPY . .

RUN mkdir -p data chroma_db /tmp/cache && chmod -R 777 /tmp/cache

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]