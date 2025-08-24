# Use the official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install FastAPI and Uvicorn
RUN pip install fastapi uvicorn pytest httpx

# Copy the FastAPI app into the container
COPY main.py .
COPY test.py .

# Expose port 80 for HTTP traffic
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]