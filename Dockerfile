# Gunakan Python 3.11 versi slim agar ringan
FROM python:3.11-slim

# Set timezone ke WIB (Asia/Jakarta)
ENV TZ=Asia/Jakarta
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /location /etc/localtime && echo $TZ > /etc/timezone

# Set folder kerja di dalam container
WORKDIR /app

# Copy requirements dan install library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kodingan bot
COPY . .

# Jalankan bot
CMD ["python", "main.py"]