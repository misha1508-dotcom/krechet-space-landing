FROM python:3.12-alpine

WORKDIR /app
COPY server.py /app/
COPY index.html /app/static/index.html
RUN mkdir -p /data

EXPOSE 80
CMD ["python3", "server.py"]
