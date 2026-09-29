# Backend FastAPI + dominio + visión.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copia los paquetes locales (monorepo) e instala en orden de dependencia.
COPY packages/contracts /app/packages/contracts
COPY services/vision /app/services/vision
COPY apps/api /app/apps/api

RUN pip install --upgrade pip \
    && pip install ./packages/contracts \
    && pip install ./services/vision \
    && pip install ./apps/api

EXPOSE 8000

CMD ["uvicorn", "chess_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
