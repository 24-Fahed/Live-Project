ARG PYTHON_BASE_IMAGE=docker.m.daocloud.io/library/python:3.10-slim
FROM ${PYTHON_BASE_IMAGE}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
