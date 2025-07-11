FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl ca-certificates nodejs npm

COPY package*.json ./
RUN npm ci && npm run build

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pollution_data_visualizer/ pollution_data_visualizer/

EXPOSE 8080
ENV PORT=8080
CMD ["gunicorn","-w","4","-k","eventlet","-b","0.0.0.0:$PORT","pollution_data_visualizer.wsgi:app"]
