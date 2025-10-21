FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev dos2unix \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn whitenoise psycopg2-binary
COPY . /app/
# 把 Windows 的 CRLF 转成 LF，避免 entrypoint.sh 在容器里报错
RUN dos2unix /app/entrypoint.sh || sed -i 's/\r$//' /app/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["bash","/app/entrypoint.sh"]
