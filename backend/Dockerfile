# ===== BASE IMAGE =====
FROM python:3.10-slim

# ===== ENV =====
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/cache

# ===== WORKDIR =====
WORKDIR /app

# ===== SYSTEM DEPENDENCIES =====
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ===== COPY REQUIREMENTS =====
COPY requirements.txt .

# ===== INSTALL PYTHON LIBS =====
RUN pip install --no-cache-dir -r requirements.txt

# ===== COPY SOURCE CODE =====
COPY . .

# ===== CREATE FOLDERS =====
RUN mkdir -p data chroma_db cache

# ===== PORT =====
EXPOSE 8000

# ===== RUN APP =====
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]