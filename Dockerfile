FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Copy the entire project
COPY environment.yml .
COPY . .

# Install Python dependencies
RUN conda env create -f environment.yml && conda clean -afy
ENV PATH=/opt/conda/envs/ontology-framework/bin:$PATH

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