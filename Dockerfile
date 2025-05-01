FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_md

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create directories for data and embeddings
RUN mkdir -p /app/data /app/temp_embeddings

# Define volumes for persistent data
VOLUME ["/app/data", "/app/temp_embeddings"]

# Run the test
CMD ["python", "-m", "tests.test_pdf_processor"] 