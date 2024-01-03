# Stage 1: Build Stage
FROM python:3.8-slim as build

# Set the working directory in the build stage
WORKDIR /app

# Copy the current directory contents into the build stage at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.8-slim

# Set the working directory in the runtime stage
WORKDIR /app

# Copy the build stage files, including the environment variables
COPY --from=build /app /app

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
