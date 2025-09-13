# # Use the official Python runtime as a parent image
# FROM python:3.12-slim

# # Set the working directory in the container
# WORKDIR /app

# # Install FastAPI and Uvicorn
# RUN pip install fastapi uvicorn pytest httpx

# # Copy the FastAPI app into the container
# COPY main.py .
# COPY test_main.py .

# # Expose port 80 for HTTP traffic
# EXPOSE 8000

# # Run the FastAPI app with Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]