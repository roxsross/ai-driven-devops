# 🤖 AI-Driven DevOps Solution

> **Transform your CI/CD pipeline with intelligent observability powered by AWS Bedrock AI**

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

This AI-Driven DevOps solution revolutionizes deployment pipelines by providing intelligent analysis and decision-making capabilities. Using AWS Bedrock's advanced AI models, it performs comprehensive health checks, analyzes system metrics, and provides actionable recommendations for deployment decisions.

### 🎯 Key Benefits

- **🧠 Intelligent Decision Making**: AI-powered analysis prevents problematic deployments
- **🚦 Multi-Stage Validation**: Pre-deployment gates, post-deployment validation, and continuous monitoring
- **📊 Comprehensive Health Scoring**: 360-degree system health assessment (0-100 scale)
- **🔄 Automated Workflows**: Seamless integration with GitHub Actions
- **🌍 Multi-Environment Support**: Production, staging, and development environments
- **📈 Proactive Monitoring**: Scheduled health checks with automated alerting

## 🚀 Quick Start

### 1. Basic Usage (Simulation Mode)
Perfect for testing without real infrastructure:

```yaml
- name: AI Observability Check
  uses: roxsross/ai-driven-devops@main
  with:
    simulation-mode: 'true'
    namespace: 'my-app'
    health-threshold: '70'
```

### 2. Production Deployment Gate
Intelligent blocking for production deployments:

```yaml
- name: AI Deployment Gate
  uses: roxsross/ai-driven-devops@main
  with:
    bedrock-model-id: 'amazon.nova-pro-v1:0'
    prometheus-url: ${{ secrets.PROMETHEUS_URL }}
    grafana-url: ${{ secrets.GRAFANA_URL }}
    namespace: 'production'
    blocking-mode: 'true'
    health-threshold: '85'
    ci-pipeline-id: ${{ github.run_id }}
    ci-environment: ${{ github.ref_name }}
    ci-commit-sha: ${{ github.sha }}
```

### 3. Post-Deployment Validation
Validate deployment success with extended monitoring:

```yaml
- name: Post-Deployment Validation
  uses: roxsross/ai-driven-devops@main
  with:
    simulation-mode: 'false'
    blocking-mode: 'false'
    health-threshold: '85'
    validation-duration: '10'  # minutes
```

## 🛠️ Workflow Types

### 🔍 Pre-Deployment Analysis
- **Purpose**: Prevent problematic deployments
- **Timing**: Before deployment execution
- **Can Block**: ✅ Yes
- **Use Cases**: PR validation, deployment gates

### ✅ Post-Deployment Validation
- **Purpose**: Validate deployment success
- **Timing**: After deployment completion
- **Can Block**: ❌ No (reports only)
- **Use Cases**: Health verification, rollback recommendations

### 📈 Continuous Monitoring
- **Purpose**: Ongoing system surveillance
- **Timing**: Scheduled (every 6 hours)
- **Can Block**: ❌ No (alerts only)
- **Use Cases**: Proactive monitoring, trend analysis

## 🎮 Complete Example Workflows

We provide ready-to-use workflow examples in the [`/examples`](./examples/) directory:

| Workflow | Purpose | Trigger | Blocking |
|----------|---------|---------|----------|
| [Pull Request Check](./examples/pull-request-check.yml) | Early feedback on code changes | PR events | No |
| [Deployment Gate](./examples/deployment-gate.yml) | Production deployment protection | Push to main | Yes |
| [Post-Deployment Validation](./examples/post-deployment-validation.yml) | Validate deployment success | Manual | No |
| [Scheduled Monitoring](./examples/ai-scheduled-monitoring.yml) | Continuous health surveillance | Cron (6h) | No |

## 📊 Health Scoring System

Our AI analyzes multiple factors to generate a comprehensive health score:

### Score Ranges
- **90-100**: 🟢 Excellent - Deploy with confidence
- **80-89**: 🟡 Good - Minor optimizations possible
- **70-79**: 🟠 Acceptable - Monitor closely
- **60-69**: 🔴 Degraded - Attention needed
- **0-59**: 🚨 Critical - Immediate action required

### Analysis Factors
1. **Application Performance** (30%): Response times, error rates, throughput
2. **Infrastructure Health** (25%): CPU, memory, disk, network metrics
3. **Kubernetes Metrics** (25%): Pod health, resource utilization, scaling
4. **Historical Trends** (20%): Performance patterns, anomaly detection

## ⚙️ Configuration

### Core Parameters
| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `simulation-mode` | Use simulated data vs real metrics | `false` | No |
| `blocking-mode` | Can block deployments on issues | `true` | No |
| `health-threshold` | Minimum health score (0-100) | `80` | No |
| `bedrock-model-id` | AWS Bedrock AI model | `amazon.nova-pro-v1:0` | Yes* |

### Integration Settings
| Parameter | Description | Required |
|-----------|-------------|----------|
| `prometheus-url` | Prometheus metrics endpoint | Optional |
| `grafana-url` | Grafana dashboard URL | Optional |
| `grafana-token` | Grafana API token | Optional |
| `telegram-bot-token` | Telegram notifications | Optional |

### Application Context
| Parameter | Description | Default |
|-----------|-------------|---------|
| `namespace` | Kubernetes namespace | `default` |
| `app-name` | Application name | Auto-detected |
| `cluster-name` | Kubernetes cluster name | Auto-detected |

## 🔐 Security & Setup

### Required Secrets
Add these to your repository secrets:

```bash
# AWS Configuration (Required for production)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model (Required)
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0

# Monitoring Integration (Optional)
PROMETHEUS_URL=https://prometheus.example.com
GRAFANA_URL=https://grafana.example.com
GRAFANA_TOKEN=your_grafana_api_token

# Notifications (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Security Best Practices
- ✅ Use GitHub Secrets for sensitive data
- ✅ Prefer AWS OIDC over access keys when possible
- ✅ Test with `simulation-mode: 'true'` first
- ✅ Start with lower health thresholds (60-70%) for testing
- ✅ Gradually increase thresholds as system matures

## 📈 Implementation Strategy

### Phase 1: Testing & Validation
1. Start with **Pull Request checks** (non-blocking)
2. Use **simulation mode** for initial testing
3. Gradually lower health thresholds

### Phase 2: Monitoring & Observability
1. Add **scheduled monitoring** workflows
2. Configure **Prometheus/Grafana** integration
3. Set up **notification channels**

### Phase 3: Production Protection
1. Implement **deployment gates** (blocking)
2. Add **post-deployment validation**
3. Fine-tune health thresholds

### Phase 4: Advanced Features
1. Multi-environment strategies
2. Custom health metrics
3. Advanced AI model configurations

## 📚 Documentation

### 🌍 Language-Specific Guides
- **🇺🇸 [Complete English Guide](README-EN.md)** - Detailed implementation guide
- **🇪🇸 [Guía Completa en Español](README-ES.md)** - Guía detallada de implementación
- **🌐 [Language Index](AI-DRIVEN-DEVOPS-GUIDE.md)** - Choose your preferred language

### 📖 Additional Resources
- [Example Workflows](./examples/) - Ready-to-use GitHub Actions workflows
- [Configuration Reference](./examples/README.md) - Detailed parameter documentation
- [Troubleshooting Guide](README-EN.md#troubleshooting) - Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch
3. **Test** your changes with simulation mode
4. **Submit** a pull request with clear description

## 🐛 Troubleshooting

### Common Issues
- **Low Health Scores**: Start with lower thresholds (60-70%)
- **AWS Permissions**: Ensure Bedrock access is enabled in your AWS account
- **Missing Metrics**: Verify Prometheus/Grafana connectivity
- **False Positives**: Tune thresholds based on your application baseline

### Getting Help
- 📖 Check our [detailed documentation](README-EN.md)
- 🐛 [Open an issue](https://github.com/roxsross/ai-driven-devops/issues) for bugs
- 💡 [Request features](https://github.com/roxsross/ai-driven-devops/issues) for enhancements
- 💬 Join our community discussions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **AWS Bedrock** for providing powerful AI capabilities
- **GitHub Actions** for seamless CI/CD integration
- **Kubernetes** community for container orchestration
- **Prometheus & Grafana** for monitoring infrastructure

---

<div align="center">

**🚀 Ready to revolutionize your DevOps pipeline with AI?**

[Get Started](./examples/) • [Documentation](README-EN.md) • [Examples](./examples/) • [Community](https://github.com/roxsross/ai-driven-devops/discussions)

**Built with ❤️ for intelligent DevOps**

*Powered by [roxsross/ai-driven-devops](https://github.com/roxsross/ai-driven-devops)*

</div>
