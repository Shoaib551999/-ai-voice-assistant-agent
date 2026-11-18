
FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends espeak-ng && \
    rm -rf /var/lib/apt/lists/*

# Install lightweight Python dependencies
RUN pip install --no-cache-dir \
    streamlit \
    groq \
    python-dotenv \
    pandas

# Copy application files
COPY app.py .
COPY database.py .
COPY agent_tools.py .
COPY agent_logger.py .
COPY log_reader.py .

# Create directories
RUN mkdir -p /app/logs

# Configure Streamlit
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
