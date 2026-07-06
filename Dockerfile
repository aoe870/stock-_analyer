FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STOCK_ANALYZER_HOST=0.0.0.0 \
    STOCK_ANALYZER_PORT=8000

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --retries 5 --timeout ${PIP_DEFAULT_TIMEOUT} -i ${PIP_INDEX_URL} -r requirements.txt

COPY stock_analyzer_app ./stock_analyzer_app
COPY public ./public
COPY db ./db

EXPOSE 8000

CMD ["python", "-m", "stock_analyzer_app"]
