FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y pandoc && \
    apt-get clean

# Set workdir and copy files
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]

