# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the entire project directory to the container
COPY ../.. .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variable to prevent bytecode generation and cache
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "configs.NER.main:app", "--host", "0.0.0.0", "--port", "8000"]
