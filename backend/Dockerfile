# dùng python nhẹ
FROM python:3.10-slim

# tạo thư mục làm việc
WORKDIR /app

# copy requirements
COPY requirements.txt .

# cài thư viện
RUN pip install --no-cache-dir -r requirements.txt

# copy code
COPY . .

# mở port
EXPOSE 8000

# chạy FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]