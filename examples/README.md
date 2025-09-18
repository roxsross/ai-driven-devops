# 📁 AI Observability Action Examples

This directory contains ready-to-use workflow examples for the AI-Driven Observability Action.

## 🚀 Quick Start

1. **Copy** the example that fits your use case
2. **Rename** it to `.github/workflows/your-workflow-name.yml` in your repository
3. **Update** `roxsross/ai-driven-devops@v1` to match your version
4. **Configure** secrets if needed (see [Configuration](#configuration))
5. **Commit** and push to trigger the workflow

## 📋 Available Examples

### 1. 🎭 [Basic Simulation](basic-simulation.yml)
- **Use case**: Testing the action without infrastructure
- **Trigger**: Push and PR
- **Features**: Simulation mode, basic health check
- **Secrets needed**: None

### 2. 🚀 [Deployment Gate](deployment-gate.yml)
- **Use case**: Block bad deployments in production
- **Trigger**: Push to main branch
- **Features**: Real AI analysis, blocking mode, full monitoring
- **Secrets needed**: AWS credentials, monitoring URLs

### 3. 🌍 [Multi-Environment](multi-environment.yml)
- **Use case**: Different settings per environment
- **Trigger**: Push to multiple branches
- **Features**: Matrix strategy, environment-specific thresholds
- **Secrets needed**: Environment-specific secrets

### 4. ⏰ [Scheduled Monitoring](scheduled-monitoring.yml)
- **Use case**: Regular health checks
- **Trigger**: Cron schedule (every 6 hours)
- **Features**: Automated monitoring, issue creation, notifications
- **Secrets needed**: AWS credentials, Telegram, GitHub token

### 5. 🔍 [Pull Request Check](pull-request-check.yml)
- **Use case**: AI feedback on pull requests
- **Trigger**: PR events
- **Features**: PR comments, non-blocking analysis
- **Secrets needed**: GitHub token (automatic)

## ⚙️ Configuration

### Required Secrets (for production examples)

Add these in your repository: **Settings** → **Secrets and variables** → **Actions**

#### AWS Configuration
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### Monitoring Integration (Optional)
```
PROMETHEUS_URL=https://your-prometheus.com
GRAFANA_URL=https://your-grafana.com
GRAFANA_TOKEN=your_grafana_api_token
```

#### Notifications (Optional)
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🎯 Usage Examples

### Basic Usage
```yaml
- name: AI Observability Check
  uses: roxsross/ai-driven-devops@v1
  with:
    simulation-mode: 'true'
    namespace: 'my-app'
    health-threshold: '70'
```

### Option 2: Published Action (Main Branch)
```yaml
- name: AI Observability Check
  uses: roxsross/ai-driven-devops@main  # ✅ Uses main branch (latest)
  with:
    simulation-mode: 'true'
    namespace: 'my-app'
    health-threshold: '70'
```

### Production Usage
```yaml
- name: AI Deployment Gate
  uses: roxsross/ai-driven-devops@v1
  with:
    bedrock-model-id: 'amazon.nova-pro-v1:0'
    prometheus-url: ${{ secrets.PROMETHEUS_URL }}
    grafana-url: ${{ secrets.GRAFANA_URL }}
    namespace: 'production'
    blocking-mode: 'true'
    health-threshold: '85'
```

## 🔧 Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   - Add `continue-on-error: true` to AWS credentials step
   - Use simulation mode for testing

2. **Missing Secrets**
   - Check secret names match exactly
   - Use simulation mode if secrets not available

3. **High Health Threshold**
   - Lower threshold for testing (60-70)
   - Increase gradually as you tune your system

---

**Happy AI-driven DevOps!** 🤖✨

*Powered by [roxsross/ai-driven-devops](https://github.com/roxsross/ai-driven-devops)*
