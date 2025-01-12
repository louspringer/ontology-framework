FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

# Install basic development tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        git \
        curl \
        wget \
        unzip \
        make \
        build-essential \
        raptor2-utils \
        rasqal-utils \
        librdf0-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure git for better credentials handling
RUN git config --system credential.helper 'cache --timeout=3600'

# Set up a non-root user (matches devcontainer.json)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Ensure the user exists
RUN if [ ! $(getent group $USER_GID) ]; then groupadd -g $USER_GID $USERNAME; fi \
    && if [ ! $(getent passwd $USER_UID) ]; then useradd -s /bin/bash -u $USER_UID -g $USER_GID -m $USERNAME; fi
