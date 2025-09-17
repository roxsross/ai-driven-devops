#!/bin/bash
set -e

# Parse arguments
SIMULATION_MODE=${1:-false}
BLOCKING_MODE=${2:-true}
HEALTH_THRESHOLD=${3:-80}

echo "🤖 AI-Driven Observability Docker Action"
echo "Simulation Mode: $SIMULATION_MODE"
echo "Blocking Mode: $BLOCKING_MODE"
echo "Health Threshold: $HEALTH_THRESHOLD"

# Configure AWS credentials if provided
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "🔐 Configuring AWS credentials..."
    aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
    aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
    aws configure set region "${AWS_REGION:-us-east-1}"
fi

# Update kubeconfig if EKS cluster is specified
if [ -n "$EKS_CLUSTER_NAME" ]; then
    echo "☸️ Updating kubeconfig for EKS cluster: $EKS_CLUSTER_NAME"
    aws eks update-kubeconfig --region "${AWS_REGION:-us-east-1}" --name "$EKS_CLUSTER_NAME" || echo "⚠️ Warning: Could not update kubeconfig"
fi

# Create .env file for the agent
echo "⚙️ Configuring environment..."
cat > .env << EOF
# AWS Configuration
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
BEDROCK_REGION=${BEDROCK_REGION:-us-east-1}
BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID:-amazon.nova-pro-v1:0}

# Monitoring Configuration
PROM_URL=$PROM_URL
GRAFANA_URL=$GRAFANA_URL
GRAFANA_TOKEN=$GRAFANA_TOKEN

# Application Configuration
NAMESPACE=${NAMESPACE:-default}
APP_NAME=$APP_NAME

# Notification Configuration
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID

# Behavior Configuration
AI_OBSERVABILITY_SIMULATION=$SIMULATION_MODE
SAFE_ACTIONS=${SAFE_ACTIONS:-rollout,scale,annotate}

# CI/CD Context
CI_PIPELINE_ID=$CI_PIPELINE_ID
CI_ENVIRONMENT=$CI_ENVIRONMENT
CI_COMMIT_SHA=$CI_COMMIT_SHA
EOF

# Run the AI agent and capture output
echo "🚀 Running AI-Driven Observability Analysis..."

# Set blocking mode environment variable
if [ "$BLOCKING_MODE" = "true" ]; then
    export BLOCKING_MODE=true
fi

# Run analysis and capture results
python3 ai-agent.py > analysis_output.txt 2>&1 || true

# Extract metrics from output
HEALTH_SCORE=$(grep -o "System Health Score: [0-9.]*" analysis_output.txt | grep -o "[0-9.]*" | head -1 || echo "0")
CRITICAL_ISSUES=$(grep -o "Critical Issues Found: [0-9]*" analysis_output.txt | grep -o "[0-9]*" | head -1 || echo "0")

# Determine recommendation
if (( $(echo "$HEALTH_SCORE >= $HEALTH_THRESHOLD" | bc -l) )) && [ "$CRITICAL_ISSUES" = "0" ]; then
    RECOMMENDATION="deploy"
    echo "✅ RECOMMENDATION: DEPLOY - System health is acceptable"
else
    RECOMMENDATION="block"
    echo "❌ RECOMMENDATION: BLOCK - System health issues detected"
fi

# Set GitHub Action outputs
echo "health-score=$HEALTH_SCORE" >> $GITHUB_OUTPUT
echo "critical-issues=$CRITICAL_ISSUES" >> $GITHUB_OUTPUT
echo "recommendation=$RECOMMENDATION" >> $GITHUB_OUTPUT

# Create analysis summary
SUMMARY="Health Score: $HEALTH_SCORE/100, Critical Issues: $CRITICAL_ISSUES, Recommendation: $RECOMMENDATION"
echo "analysis-summary=$SUMMARY" >> $GITHUB_OUTPUT

# Show full output
echo "📊 Analysis Results:"
cat analysis_output.txt

# Exit with error if blocking and issues found
if [ "$BLOCKING_MODE" = "true" ] && [ "$RECOMMENDATION" = "block" ]; then
    echo "🚫 Blocking deployment due to critical issues"
    exit 1
fi

echo "✅ AI Observability analysis completed successfully"
