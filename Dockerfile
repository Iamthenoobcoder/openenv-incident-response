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

# Expose the API port
EXPOSE 7860

# The main entrypoint starts the FastAPI server
CMD ["python", "server/app.py"]
