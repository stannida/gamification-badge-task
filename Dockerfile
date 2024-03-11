FROM python:3.8.2

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install -r requirements.txt

# EXPOSE 8502
HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health
CMD ["streamlit", "run", "dashboard.py", "--server.port=8502", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]