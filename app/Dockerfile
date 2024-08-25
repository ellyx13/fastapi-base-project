# Use an official lightweight Python image.
FROM python:3.12-alpine

# Set the working directory.
WORKDIR /opt/projects/app

# Set environment variables to prevent Python from writing pyc files to disk
# and ensure that Python output is logged directly to the terminal.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apk add --no-cache curl \
    && apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev python3-dev build-base \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && rm -rf /root/.cache/pip

# Copy the requirements file and install Python dependencies.
# Use --no-cache-dir to prevent pip from saving the cache, which reduces image size.
# After installing Python dependencies, remove the build dependencies to reduce the final image size (apk del .build-deps).
# This is important because some dependencies are only needed for building wheel files and are not necessary afterwards.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copy the rest of the application.
COPY . .