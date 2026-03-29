ARG PYTHON_BASE_IMAGE=docker.m.daocloud.io/library/python:3.10-slim
FROM ${PYTHON_BASE_IMAGE}

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} -r requirements.txt

COPY . .

EXPOSE 8080 443

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
