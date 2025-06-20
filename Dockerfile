FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY www/ ./www/
COPY .env.example ./.env
COPY scripts/start.sh ./scripts/start.sh

# Make sure scripts are executable
RUN chmod +x ./scripts/start.sh

# Create logs directory for app logs
RUN mkdir -p logs

# Create data directory and make it writable
RUN mkdir -p data
RUN chmod 777 data

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "src.app"]
