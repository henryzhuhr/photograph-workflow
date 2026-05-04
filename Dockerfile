# Stage 1: Build Vue frontend
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY apps/web/frontend/package.json apps/web/frontend/package-lock.json ./
RUN npm ci
COPY apps/web/frontend/ ./
RUN npm run build

# Stage 2: Python backend + static files
FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ ./src/
COPY apps/ ./apps/
COPY --from=frontend-build /frontend/dist ./apps/web/frontend/dist

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "apps.web.backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
