FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace/backend

COPY backend/requirements.txt /tmp/requirements.txt
COPY docker/backend/entrypoint.sh /usr/local/bin/backend-entrypoint.sh

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && chmod +x /usr/local/bin/backend-entrypoint.sh

COPY backend /workspace/backend

ENTRYPOINT ["backend-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
