FROM gitpod/workspace-full

# Add GUI dependencies first
RUN sudo apt-get update && sudo apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6

# Clean up APT cache to save space
RUN sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

# Download and install Miniforge
RUN wget -q https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O miniforge.sh && \
    sudo bash miniforge.sh -b -p /opt/conda && \
    sudo rm miniforge.sh && \
    sudo find /opt/conda/ -follow -type f -name '*.a' -delete && \
    sudo find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    sudo rm -rf /opt/conda/pkgs/

# Add conda to path and initialize
ENV PATH="/opt/conda/bin:${PATH}"

# Initialize conda and create persistence script
RUN conda init bash && \
    conda clean -afy && \
    sudo chown -R gitpod:gitpod /opt/conda && \
    # Create persistence script
    echo 'create-overlay /opt/conda' > "$HOME/.runonce/1-conda"