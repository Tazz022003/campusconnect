# Use official Python image as a base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Run the application (using Django's built-in server for now)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]