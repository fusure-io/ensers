# Stage 1: Build Stage
FROM python:3.8-slim 

# Set working directory
WORKDIR /app

# Copy contents
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5001

# Run app
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
