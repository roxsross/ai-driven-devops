FROM python:3.12-slim

# Set build arguments for multi-arch support
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl (multi-arch)
RUN KUBECTL_ARCH=$(case ${TARGETPLATFORM} in \
        "linux/amd64") echo "amd64" ;; \
        "linux/arm64") echo "arm64" ;; \
        *) echo "amd64" ;; \
    esac) && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${KUBECTL_ARCH}/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Install AWS CLI (multi-arch)
RUN AWS_ARCH=$(case ${TARGETPLATFORM} in \
        "linux/amd64") echo "x86_64" ;; \
        "linux/arm64") echo "aarch64" ;; \
        *) echo "x86_64" ;; \
    esac) && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Copy and set up entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]