FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg62-turbo \
    zlib1g \
    libgl1 \
    libgomp1 \
  && rm -rf /var/lib/apt/lists/*

COPY search_api/requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r /srv/requirements.txt

COPY app /srv/app

COPY search_api /srv/search_api

ENV PYTHONPATH=/srv

EXPOSE 8000

CMD ["uvicorn", "search_api.main:app", "--host", "0.0.0.0", "--port", "7777"]
