FROM gitpod/workspace-full

# Install custom tools, runtime, etc.
# Download and install Anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh -O anaconda.sh && \
    bash anaconda.sh -b -p /opt/conda && \
    rm anaconda.sh

# Add conda to path
ENV PATH="/opt/conda/bin:${PATH}"

# Initialize conda for shell interaction
RUN conda init bash