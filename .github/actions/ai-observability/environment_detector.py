#!/usr/bin/env python3
"""
Smart Environment Detection for AI-Driven Observability
Automatically detects and configures the best monitoring approach based on available infrastructure
"""

import os
import json
import subprocess
import requests
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EnvironmentType(Enum):
    GITHUB_ACTIONS = "github_actions"
    AWS_EKS = "aws_eks"
    GOOGLE_GKE = "google_gke"
    AZURE_AKS = "azure_aks"
    LOCAL_KUBERNETES = "local_k8s"
    DOCKER_DESKTOP = "docker_desktop"
    SIMULATION = "simulation"
    UNKNOWN = "unknown"

@dataclass
class EnvironmentConfig:
    env_type: EnvironmentType
    kubernetes_available: bool
    cloud_provider: Optional[str]
    monitoring_endpoints: Dict[str, str]
    auth_method: str
    capabilities: Dict[str, bool]
    recommendations: Dict[str, Any]

class SmartEnvironmentDetector:
    """
    Intelligently detects the runtime environment and configures monitoring accordingly
    """
    
    def __init__(self):
        self.config = None
        self._detection_cache = {}
    
    def detect_environment(self) -> EnvironmentConfig:
        """
        Main detection logic - tries multiple detection methods
        """
        print("🔍 Detecting environment automatically...")
        
        # Check cache first
        if self.config:
            return self.config
        
        # Detection pipeline
        detectors = [
            self._detect_github_actions,
            self._detect_aws_eks,
            self._detect_google_gke,
            self._detect_azure_aks,
            self._detect_local_kubernetes,
            self._detect_docker_desktop,
            self._detect_simulation_mode
        ]
        
        for detector in detectors:
            try:
                config = detector()
                if config:
                    self.config = config
                    print(f"✅ Detected environment: {config.env_type.value}")
                    return config
            except Exception as e:
                print(f"⚠️  Detector failed: {detector.__name__}: {e}")
                continue
        
        # Fallback to unknown environment
        self.config = self._create_unknown_config()
        print("❓ Unknown environment - using simulation mode")
        return self.config
    
    def _detect_github_actions(self) -> Optional[EnvironmentConfig]:
        """Detect if running in GitHub Actions"""
        if not os.getenv("GITHUB_ACTIONS"):
            return None
        
        print("🐙 GitHub Actions environment detected")
        
        # Check if we have cluster access
        k8s_available = self._check_kubernetes_access()
        
        # Determine monitoring strategy
        if k8s_available:
            monitoring_endpoints = self._get_cluster_monitoring_endpoints()
            auth_method = "service_account"
        else:
            # Use external monitoring or simulation
            monitoring_endpoints = self._get_external_monitoring_endpoints()
            auth_method = "api_key"
        
        return EnvironmentConfig(
            env_type=EnvironmentType.GITHUB_ACTIONS,
            kubernetes_available=k8s_available,
            cloud_provider=self._detect_cloud_provider(),
            monitoring_endpoints=monitoring_endpoints,
            auth_method=auth_method,
            capabilities={
                "real_time_monitoring": k8s_available,
                "predictive_analytics": True,
                "chaos_simulation": k8s_available,
                "external_notifications": True,
                "ci_cd_integration": True
            },
            recommendations={
                "setup_complexity": "low" if not k8s_available else "medium",
                "suggested_approach": "external_monitoring" if not k8s_available else "direct_cluster",
                "next_steps": self._get_github_actions_recommendations(k8s_available)
            }
        )
    
    def _detect_aws_eks(self) -> Optional[EnvironmentConfig]:
        """Detect AWS EKS environment"""
        # Check for AWS credentials and EKS indicators
        if not (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ROLE_ARN")):
            return None
        
        # Try to detect EKS cluster
        try:
            # Check if we're running inside EKS
            if self._is_running_in_eks():
                print("☁️  AWS EKS environment detected")
                
                return EnvironmentConfig(
                    env_type=EnvironmentType.AWS_EKS,
                    kubernetes_available=True,
                    cloud_provider="aws",
                    monitoring_endpoints=self._get_aws_monitoring_endpoints(),
                    auth_method="iam_role",
                    capabilities={
                        "real_time_monitoring": True,
                        "predictive_analytics": True,
                        "chaos_simulation": True,
                        "external_notifications": True,
                        "ci_cd_integration": True,
                        "aws_integration": True,
                        "cloudwatch_metrics": True
                    },
                    recommendations={
                        "setup_complexity": "low",
                        "suggested_approach": "native_aws",
                        "next_steps": [
                            "Use IAM roles for service accounts (IRSA)",
                            "Enable CloudWatch Container Insights",
                            "Configure AWS Load Balancer Controller"
                        ]
                    }
                )
        except Exception:
            pass
        
        return None
    
    def _detect_google_gke(self) -> Optional[EnvironmentConfig]:
        """Detect Google GKE environment"""
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not self._is_running_in_gke():
            return None
        
        print("☁️  Google GKE environment detected")
        
        return EnvironmentConfig(
            env_type=EnvironmentType.GOOGLE_GKE,
            kubernetes_available=True,
            cloud_provider="gcp",
            monitoring_endpoints=self._get_gcp_monitoring_endpoints(),
            auth_method="workload_identity",
            capabilities={
                "real_time_monitoring": True,
                "predictive_analytics": True,
                "chaos_simulation": True,
                "external_notifications": True,
                "ci_cd_integration": True,
                "gcp_integration": True,
                "stackdriver_metrics": True
            },
            recommendations={
                "setup_complexity": "low",
                "suggested_approach": "native_gcp",
                "next_steps": [
                    "Enable Workload Identity",
                    "Configure GKE monitoring",
                    "Use Google Cloud Operations suite"
                ]
            }
        )
    
    def _detect_azure_aks(self) -> Optional[EnvironmentConfig]:
        """Detect Azure AKS environment"""
        if not (os.getenv("AZURE_CLIENT_ID") or self._is_running_in_aks()):
            return None
        
        print("☁️  Azure AKS environment detected")
        
        return EnvironmentConfig(
            env_type=EnvironmentType.AZURE_AKS,
            kubernetes_available=True,
            cloud_provider="azure",
            monitoring_endpoints=self._get_azure_monitoring_endpoints(),
            auth_method="managed_identity",
            capabilities={
                "real_time_monitoring": True,
                "predictive_analytics": True,
                "chaos_simulation": True,
                "external_notifications": True,
                "ci_cd_integration": True,
                "azure_integration": True,
                "azure_monitor": True
            },
            recommendations={
                "setup_complexity": "low",
                "suggested_approach": "native_azure",
                "next_steps": [
                    "Enable Azure AD Pod Identity",
                    "Configure Azure Monitor for containers",
                    "Use Azure Application Insights"
                ]
            }
        )
    
    def _detect_local_kubernetes(self) -> Optional[EnvironmentConfig]:
        """Detect local Kubernetes (minikube, kind, etc.)"""
        if not self._check_kubernetes_access():
            return None
        
        # Check if it's a local cluster
        try:
            result = subprocess.run(
                ["kubectl", "cluster-info"], 
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                cluster_info = result.stdout.lower()
                
                # Detect local cluster types
                if any(local_indicator in cluster_info for local_indicator in 
                       ["127.0.0.1", "localhost", "minikube", "kind", "docker-desktop"]):
                    
                    print("🏠 Local Kubernetes environment detected")
                    
                    return EnvironmentConfig(
                        env_type=EnvironmentType.LOCAL_KUBERNETES,
                        kubernetes_available=True,
                        cloud_provider=None,
                        monitoring_endpoints=self._get_local_monitoring_endpoints(),
                        auth_method="kubeconfig",
                        capabilities={
                            "real_time_monitoring": True,
                            "predictive_analytics": True,
                            "chaos_simulation": True,
                            "external_notifications": True,
                            "ci_cd_integration": False,
                            "local_development": True
                        },
                        recommendations={
                            "setup_complexity": "medium",
                            "suggested_approach": "local_stack",
                            "next_steps": [
                                "Install Prometheus and Grafana locally",
                                "Configure port-forwarding for monitoring",
                                "Use local storage for metrics"
                            ]
                        }
                    )
        except Exception:
            pass
        
        return None
    
    def _detect_docker_desktop(self) -> Optional[EnvironmentConfig]:
        """Detect Docker Desktop with Kubernetes"""
        try:
            # Check if Docker Desktop is running
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and "docker desktop" in result.stdout.lower():
                k8s_available = self._check_kubernetes_access()
                
                print("🐳 Docker Desktop environment detected")
                
                return EnvironmentConfig(
                    env_type=EnvironmentType.DOCKER_DESKTOP,
                    kubernetes_available=k8s_available,
                    cloud_provider=None,
                    monitoring_endpoints=self._get_docker_desktop_endpoints(),
                    auth_method="kubeconfig" if k8s_available else "docker_api",
                    capabilities={
                        "real_time_monitoring": k8s_available,
                        "predictive_analytics": True,
                        "chaos_simulation": k8s_available,
                        "external_notifications": True,
                        "ci_cd_integration": False,
                        "local_development": True,
                        "docker_integration": True
                    },
                    recommendations={
                        "setup_complexity": "low",
                        "suggested_approach": "docker_compose" if not k8s_available else "local_k8s",
                        "next_steps": [
                            "Enable Kubernetes in Docker Desktop" if not k8s_available else "Deploy monitoring stack",
                            "Use docker-compose for monitoring services",
                            "Configure local development workflow"
                        ]
                    }
                )
        except Exception:
            pass
        
        return None
    
    def _detect_simulation_mode(self) -> Optional[EnvironmentConfig]:
        """Fallback simulation mode for testing"""
        if os.getenv("AI_OBSERVABILITY_SIMULATION", "false").lower() == "true":
            print("🎭 Simulation mode enabled")
            
            return EnvironmentConfig(
                env_type=EnvironmentType.SIMULATION,
                kubernetes_available=False,
                cloud_provider=None,
                monitoring_endpoints=self._get_simulation_endpoints(),
                auth_method="none",
                capabilities={
                    "real_time_monitoring": False,
                    "predictive_analytics": True,
                    "chaos_simulation": True,
                    "external_notifications": True,
                    "ci_cd_integration": True,
                    "simulation_mode": True
                },
                recommendations={
                    "setup_complexity": "minimal",
                    "suggested_approach": "simulation",
                    "next_steps": [
                        "Perfect for testing AI observability features",
                        "No infrastructure required",
                        "Use for CI/CD pipeline validation"
                    ]
                }
            )
        
        return None
    
    def _create_unknown_config(self) -> EnvironmentConfig:
        """Create configuration for unknown environment"""
        return EnvironmentConfig(
            env_type=EnvironmentType.UNKNOWN,
            kubernetes_available=False,
            cloud_provider=None,
            monitoring_endpoints=self._get_simulation_endpoints(),
            auth_method="none",
            capabilities={
                "real_time_monitoring": False,
                "predictive_analytics": True,
                "chaos_simulation": False,
                "external_notifications": True,
                "ci_cd_integration": True,
                "simulation_mode": True
            },
            recommendations={
                "setup_complexity": "minimal",
                "suggested_approach": "simulation",
                "next_steps": [
                    "Environment auto-detection failed",
                    "Using simulation mode as fallback",
                    "Consider manual configuration for full features"
                ]
            }
        )
    
    # Helper methods for detection
    def _check_kubernetes_access(self) -> bool:
        """Check if kubectl is available and working"""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"], 
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _detect_cloud_provider(self) -> Optional[str]:
        """Detect cloud provider from environment"""
        if os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"):
            return "aws"
        elif os.getenv("GOOGLE_CLOUD_PROJECT"):
            return "gcp"
        elif os.getenv("AZURE_SUBSCRIPTION_ID"):
            return "azure"
        return None
    
    def _is_running_in_eks(self) -> bool:
        """Check if running inside EKS"""
        try:
            # Check for EKS-specific environment indicators
            if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount"):
                # Try to get cluster info
                result = subprocess.run(
                    ["kubectl", "get", "nodes", "-o", "jsonpath={.items[0].spec.providerID}"],
                    capture_output=True, text=True, timeout=5
                )
                return "aws" in result.stdout.lower()
        except Exception:
            pass
        return False
    
    def _is_running_in_gke(self) -> bool:
        """Check if running inside GKE"""
        try:
            # Check GKE metadata server
            response = requests.get(
                "http://metadata.google.internal/computeMetadata/v1/instance/attributes/cluster-name",
                headers={"Metadata-Flavor": "Google"},
                timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _is_running_in_aks(self) -> bool:
        """Check if running inside AKS"""
        try:
            # Check for AKS-specific indicators
            if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount"):
                result = subprocess.run(
                    ["kubectl", "get", "nodes", "-o", "jsonpath={.items[0].spec.providerID}"],
                    capture_output=True, text=True, timeout=5
                )
                return "azure" in result.stdout.lower()
        except Exception:
            pass
        return False
    
    # Monitoring endpoints configuration
    def _get_cluster_monitoring_endpoints(self) -> Dict[str, str]:
        """Get monitoring endpoints from cluster"""
        endpoints = {}
        
        # Try to find Prometheus
        try:
            result = subprocess.run(
                ["kubectl", "get", "svc", "-A", "-o", "json"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                services = json.loads(result.stdout)
                for service in services.get("items", []):
                    name = service["metadata"]["name"].lower()
                    namespace = service["metadata"]["namespace"]
                    
                    if "prometheus" in name:
                        endpoints["prometheus"] = f"http://{name}.{namespace}.svc.cluster.local"
                    elif "grafana" in name:
                        endpoints["grafana"] = f"http://{name}.{namespace}.svc.cluster.local"
        except Exception:
            pass
        
        return endpoints
    
    def _get_external_monitoring_endpoints(self) -> Dict[str, str]:
        """Get external monitoring endpoints"""
        return {
            "prometheus": os.getenv("PROM_URL", ""),
            "grafana": os.getenv("GRAFANA_URL", ""),
            "external": True
        }
    
    def _get_aws_monitoring_endpoints(self) -> Dict[str, str]:
        """Get AWS-specific monitoring endpoints"""
        region = os.getenv("AWS_REGION", "us-east-1")
        return {
            "cloudwatch": f"https://monitoring.{region}.amazonaws.com",
            "prometheus": os.getenv("PROM_URL", ""),
            "grafana": os.getenv("GRAFANA_URL", ""),
            "aws_native": True
        }
    
    def _get_gcp_monitoring_endpoints(self) -> Dict[str, str]:
        """Get GCP-specific monitoring endpoints"""
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        return {
            "stackdriver": f"https://monitoring.googleapis.com/v1/projects/{project}",
            "prometheus": os.getenv("PROM_URL", ""),
            "grafana": os.getenv("GRAFANA_URL", ""),
            "gcp_native": True
        }
    
    def _get_azure_monitoring_endpoints(self) -> Dict[str, str]:
        """Get Azure-specific monitoring endpoints"""
        return {
            "azure_monitor": "https://management.azure.com",
            "prometheus": os.getenv("PROM_URL", ""),
            "grafana": os.getenv("GRAFANA_URL", ""),
            "azure_native": True
        }
    
    def _get_local_monitoring_endpoints(self) -> Dict[str, str]:
        """Get local monitoring endpoints"""
        return {
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3000",
            "local": True
        }
    
    def _get_docker_desktop_endpoints(self) -> Dict[str, str]:
        """Get Docker Desktop monitoring endpoints"""
        return {
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3000",
            "docker_api": "unix:///var/run/docker.sock",
            "docker_desktop": True
        }
    
    def _get_simulation_endpoints(self) -> Dict[str, str]:
        """Get simulation mode endpoints"""
        return {
            "simulation": True,
            "mock_prometheus": "http://mock-prometheus",
            "mock_grafana": "http://mock-grafana"
        }
    
    def _get_github_actions_recommendations(self, k8s_available: bool) -> list:
        """Get GitHub Actions specific recommendations"""
        if k8s_available:
            return [
                "Cluster access detected - using direct monitoring",
                "Configure RBAC for GitHub Actions service account",
                "Use secrets for sensitive monitoring endpoints"
            ]
        else:
            return [
                "No cluster access - using external monitoring",
                "Perfect for validating deployment readiness",
                "Consider using simulation mode for testing"
            ]
    
    def get_setup_instructions(self) -> Dict[str, Any]:
        """Get setup instructions based on detected environment"""
        if not self.config:
            self.detect_environment()
        
        instructions = {
            "environment": self.config.env_type.value,
            "complexity": self.config.recommendations["setup_complexity"],
            "approach": self.config.recommendations["suggested_approach"],
            "steps": self.config.recommendations["next_steps"],
            "required_secrets": self._get_required_secrets(),
            "optional_configs": self._get_optional_configs(),
            "example_usage": self._get_example_usage()
        }
        
        return instructions
    
    def _get_required_secrets(self) -> Dict[str, str]:
        """Get required secrets based on environment"""
        base_secrets = {
            "BEDROCK_REGION": "AWS region for Bedrock (e.g., us-east-1)",
            "BEDROCK_MODEL_ID": "Bedrock model ID (e.g., us.anthropic.claude-sonnet-4-20250514-v1:0)"
        }
        
        if self.config.cloud_provider == "aws":
            base_secrets.update({
                "AWS_ACCESS_KEY_ID": "AWS access key (or use IAM roles)",
                "AWS_SECRET_ACCESS_KEY": "AWS secret key (or use IAM roles)"
            })
        elif self.config.cloud_provider == "gcp":
            base_secrets.update({
                "GOOGLE_APPLICATION_CREDENTIALS": "Path to GCP service account key"
            })
        elif self.config.cloud_provider == "azure":
            base_secrets.update({
                "AZURE_CLIENT_ID": "Azure client ID",
                "AZURE_CLIENT_SECRET": "Azure client secret",
                "AZURE_TENANT_ID": "Azure tenant ID"
            })
        
        if not self.config.kubernetes_available:
            base_secrets.update({
                "PROM_URL": "External Prometheus URL (optional)",
                "GRAFANA_URL": "External Grafana URL (optional)"
            })
        
        return base_secrets
    
    def _get_optional_configs(self) -> Dict[str, str]:
        """Get optional configurations"""
        return {
            "TELEGRAM_BOT_TOKEN": "For notifications (optional)",
            "TELEGRAM_CHAT_ID": "For notifications (optional)",
            "NAMESPACE": "Kubernetes namespace to monitor (default: default)",
            "AI_OBSERVABILITY_SIMULATION": "Enable simulation mode (true/false)"
        }
    
    def _get_example_usage(self) -> str:
        """Get example usage based on environment"""
        if self.config.env_type == EnvironmentType.GITHUB_ACTIONS:
            return """
# Example GitHub Actions workflow
- name: AI Observability Check
  uses: your-org/ai-observability-action@v1
  with:
    namespace: 'production'
    environment: 'prod'
    blocking-mode: 'true'
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    BEDROCK_REGION: 'us-east-1'
    BEDROCK_MODEL_ID: 'us.anthropic.claude-sonnet-4-20250514-v1:0'
"""
        elif self.config.env_type == EnvironmentType.SIMULATION:
            return """
# Example simulation mode
- name: AI Observability Simulation
  uses: your-org/ai-observability-action@v1
  with:
    namespace: 'test'
    environment: 'simulation'
  env:
    AI_OBSERVABILITY_SIMULATION: 'true'
    BEDROCK_REGION: 'us-east-1'
    BEDROCK_MODEL_ID: 'us.anthropic.claude-sonnet-4-20250514-v1:0'
"""
        else:
            return f"""
# Example for {self.config.env_type.value}
- name: AI Observability Check
  uses: your-org/ai-observability-action@v1
  with:
    namespace: 'production'
    environment: 'prod'
    auto-detect: 'true'
"""

# Usage example
if __name__ == "__main__":
    detector = SmartEnvironmentDetector()
    config = detector.detect_environment()
    
    print("\n" + "="*80)
    print("🎯 ENVIRONMENT DETECTION COMPLETE")
    print("="*80)
    
    print(f"Environment Type: {config.env_type.value}")
    print(f"Kubernetes Available: {config.kubernetes_available}")
    print(f"Cloud Provider: {config.cloud_provider or 'None'}")
    print(f"Auth Method: {config.auth_method}")
    
    print(f"\n🚀 Capabilities:")
    for capability, enabled in config.capabilities.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {capability}")
    
    print(f"\n📋 Setup Instructions:")
    instructions = detector.get_setup_instructions()
    print(f"  Complexity: {instructions['complexity']}")
    print(f"  Approach: {instructions['approach']}")
    
    print(f"\n📝 Next Steps:")
    for step in instructions['steps']:
        print(f"  • {step}")
