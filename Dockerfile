FROM python:3.12-slim

# Set build arguments for multi-arch support
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install system dependencies (silenced)
RUN apt-get update > /dev/null 2>&1 && apt-get install -y \
    curl \
    unzip \
    ca-certificates \
    > /dev/null 2>&1 && \
    rm -rf /var/lib/apt/lists/* && \
    echo "✓ System dependencies installed"

# Install kubectl (multi-arch, silenced)
RUN KUBECTL_ARCH=$(case ${TARGETPLATFORM} in \
        "linux/amd64") echo "amd64" ;; \
        "linux/arm64") echo "arm64" ;; \
        *) echo "amd64" ;; \
    esac) && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${KUBECTL_ARCH}/kubectl" 2>/dev/null && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/ && \
    echo "✓ kubectl installed"

# Install AWS CLI (multi-arch, silenced)
RUN AWS_ARCH=$(case ${TARGETPLATFORM} in \
        "linux/amd64") echo "x86_64" ;; \
        "linux/arm64") echo "aarch64" ;; \
        *) echo "x86_64" ;; \
    esac) && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o "awscliv2.zip" 2>/dev/null && \
    unzip -q awscliv2.zip && \
    ./aws/install --install-dir /usr/local/aws-cli --bin-dir /usr/local/bin > /dev/null 2>&1 && \
    rm -rf aws awscliv2.zip && \
    echo "✓ AWS CLI installed"

WORKDIR /app

# Copy requirements and install Python dependencies (silenced)
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --disable-pip-version-check -r requirements.txt && \
    echo "✓ Python dependencies installed"

# Copy agent code
COPY . .

# Copy and set up entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]