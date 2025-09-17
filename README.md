# 🤖 AI-Driven Observability Action

Transform your CI/CD with intelligent observability powered by AWS Bedrock and advanced AI analysis.

## 🚀 Quick Start

### Basic Usage (Simulation Mode)
```yaml
- name: AI Observability Check
  uses: your-org/ai-observability@v1
  with:
    simulation-mode: 'true'
    namespace: 'my-app'
    health-threshold: '70'
```

### Production Usage
```yaml
- name: AI Deployment Gate
  uses: your-org/ai-observability@v1
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
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 🎯 Features

- 🧠 **AI-Powered Analysis**: Uses AWS Bedrock (Nova Pro, Claude Sonnet 4) for intelligent insights
- 🔍 **Smart Environment Detection**: Auto-detects EKS, GKE, AKS, Docker Desktop, or local setups
- 🎭 **Simulation Mode**: Test without real infrastructure
- 📊 **Real Monitoring**: Integrates with Prometheus and Grafana
- 🚨 **Intelligent Blocking**: Automatically blocks bad deployments
- 📱 **Smart Notifications**: Context-aware Telegram alerts

## 📋 Key Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `simulation-mode` | Run without real infrastructure | `false` |
| `blocking-mode` | Block deployment on critical issues | `true` |
| `health-threshold` | Minimum health score (0-100) | `80` |
| `bedrock-model-id` | AWS Bedrock model | `amazon.nova-pro-v1:0` |
| `namespace` | Kubernetes namespace | `default` |
| `prometheus-url` | Prometheus endpoint | - |
| `grafana-url` | Grafana endpoint | - |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `health-score` | System health score (0-100) |
| `critical-issues` | Number of critical issues found |
| `recommendation` | AI recommendation (`deploy` or `block`) |
| `analysis-summary` | Summary of the analysis |

## 🔧 Examples

See [.github/workflows/ai-gate-example.yml](.github/workflows/ai-gate-example.yml) for complete examples including:
- Simulation mode testing
- Production deployment gates
- Multi-environment strategies

## 🛡️ Security

- Use GitHub Secrets for sensitive data
- Prefer AWS OIDC over access keys
- Test with `simulation-mode: 'true'` first

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ for intelligent DevOps**
