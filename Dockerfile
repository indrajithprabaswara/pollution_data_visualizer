FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package*.json ./
RUN apt-get update && apt-get install -y curl ca-certificates nodejs npm \
    && npm ci && npm run build

COPY . .
EXPOSE 8080
ENV PORT=8080
CMD ["gunicorn","-w","4","-k","eventlet","-b","0.0.0.0:$PORT","pollution_data_visualizer.wsgi:app"]
