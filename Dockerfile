# Use PyTorch official image (PyTorch already installed!)
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /chatbot

# Install Java for VnCoreNLP + build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    build-essential \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/

# Copy requirements (without torch since it's pre-installed)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /chatbot

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

# Use gunicorn for production
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app:app