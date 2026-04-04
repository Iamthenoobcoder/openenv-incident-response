# Stage 1: Build the Vite + React frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Install dependencies first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy necessary frontend files and build
COPY tsconfig.json vite.config.ts index.html ./
COPY src/ ./src/
RUN npm run build

# Stage 2: Build the Python backend and serve
FROM python:3.11-slim
WORKDIR /app

# Set environment variables for better standard out viewing
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code into the container
# .dockerignore will prevent .venv, node_modules, and dist from being copied
COPY . .

# Copy the built dist directory from the frontend stage
COPY --from=frontend-builder /app/dist ./dist

# Expose the API port
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:7860/api/health || exit 1

# The main entrypoint starts the FastAPI server
CMD ["python", "server/app.py"]
