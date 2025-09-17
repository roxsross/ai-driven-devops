#!/usr/bin/env python3
"""
AI-Driven Observability Agent for CI/CD Environments
AWS re:Invent 2025 Demo - "Supercharge DevOps with AI-driven observability"

This agent demonstrates how Generative AI transforms DevOps and SRE practices by:
- Automatically explaining failures with context
- Correlating events across metrics, logs, and traces  
- Providing predictive recommendations
- Enabling proactive insights with clear traceability
- Enhancing automation and incident response capabilities
"""

import os, time, json, requests, subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from environment_detector import SmartEnvironmentDetector, EnvironmentType

# Load environment variables
load_dotenv()

# ---- Smart Environment Detection ----
print("🔍 Initializing Smart Environment Detection...")
env_detector = SmartEnvironmentDetector()
env_config = env_detector.detect_environment()

# ---- Dynamic Configuration Based on Environment ----
# Base configuration
NAMESPACE = os.getenv("NAMESPACE", "default")
SAFE_ACTIONS = set(filter(None, os.getenv("SAFE_ACTIONS", "").split(",")))

# Smart endpoint configuration - prioritize .env file over auto-detection
PROM_URL = os.getenv("PROM_URL", "")
GRAFANA_URL = os.getenv("GRAFANA_URL", "")

# Only use auto-detected endpoints if not configured in .env
if not PROM_URL and env_config.monitoring_endpoints.get("prometheus"):
    PROM_URL = env_config.monitoring_endpoints["prometheus"]
    
if not GRAFANA_URL and env_config.monitoring_endpoints.get("grafana"):
    GRAFANA_URL = env_config.monitoring_endpoints["grafana"]

# Environment-specific adjustments
if env_config.env_type == EnvironmentType.SIMULATION:
    print("🎭 Simulation mode detected - using mock endpoints")
    PROM_URL = "http://mock-prometheus"
    GRAFANA_URL = "http://mock-grafana"
elif env_config.env_type in [EnvironmentType.AWS_EKS, EnvironmentType.GOOGLE_GKE, EnvironmentType.AZURE_AKS]:
    print(f"☁️  Cloud environment detected: {env_config.env_type.value}")
elif env_config.env_type == EnvironmentType.GITHUB_ACTIONS:
    print("🐙 GitHub Actions environment detected")

print(f"📊 Monitoring endpoints configured:")
print(f"   Prometheus: {PROM_URL or 'Not configured'}")
print(f"   Grafana: {GRAFANA_URL or 'Not configured'}")
print(f"   Kubernetes: {'Available' if env_config.kubernetes_available else 'Not available'}")
print(f"   Auth Method: {env_config.auth_method}")

# Bedrock Configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

# Telegram Configuration for CI/CD Notifications
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# CI/CD Context
CI_PIPELINE_ID = os.getenv("CI_PIPELINE_ID", "manual-execution")
CI_COMMIT_SHA = os.getenv("CI_COMMIT_SHA", "unknown")
CI_ENVIRONMENT = os.getenv("CI_ENVIRONMENT", "development")

# Initialize Bedrock model only if we have AWS credentials or simulation mode
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
simulation_mode = os.getenv("AI_OBSERVABILITY_SIMULATION", "false").lower() == "true"

# Check for AWS credentials in ~/.aws/credentials if not in environment
if not aws_access_key or not aws_secret_key:
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            aws_access_key = credentials.access_key
            aws_secret_key = credentials.secret_key
            print("✅ AWS credentials found in ~/.aws/credentials")
    except Exception as e:
        print(f"⚠️  Could not load AWS credentials: {e}")

if simulation_mode:
    print("🎭 Simulation mode enabled - AI model will be mocked")
    model = None  # We'll handle this in the agent creation
elif aws_access_key and aws_secret_key:
    print("🤖 AWS Bedrock model initialized")
    model = BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        region_name=BEDROCK_REGION,
        temperature=0.1
    )
else:
    print("⚠️  No AWS credentials found - enabling simulation mode")
    simulation_mode = True
    os.environ["AI_OBSERVABILITY_SIMULATION"] = "true"
    model = None

# ---- AI-Driven Observability Tools ----

@tool
def analyze_system_health() -> Dict[str, Any]:
    """
    AI-Enhanced System Health Analysis with Smart Environment Detection
    Adapts analysis based on detected environment capabilities
    """
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "environment_info": {
            "type": env_config.env_type.value,
            "kubernetes_available": env_config.kubernetes_available,
            "cloud_provider": env_config.cloud_provider,
            "auth_method": env_config.auth_method,
            "capabilities": env_config.capabilities
        },
        "pipeline_context": {
            "pipeline_id": CI_PIPELINE_ID,
            "commit_sha": CI_COMMIT_SHA,
            "environment": CI_ENVIRONMENT
        },
        "health_score": 100,
        "pods": {},
        "ai_insights": [],
        "predictions": [],
        "correlations": [],
        "recommendations": [],
        "traceability": []
    }
    
    try:
        # Adapt analysis based on environment capabilities
        if env_config.env_type == EnvironmentType.SIMULATION:
            return _generate_simulation_health_analysis(analysis)
        elif not env_config.kubernetes_available:
            return _generate_external_health_analysis(analysis)
        
        # Get comprehensive pod status for Kubernetes environments
        cmd = ["kubectl", "get", "pods", "-n", NAMESPACE, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            pods_data = json.loads(result.stdout)
            total_pods = len(pods_data.get("items", []))
            ready_pods = 0
            
            for pod in pods_data.get("items", []):
                pod_name = pod["metadata"]["name"]
                pod_status = pod["status"]
                
                # Enhanced pod analysis
                ready = False
                if "conditions" in pod_status:
                    for condition in pod_status["conditions"]:
                        if condition["type"] == "Ready" and condition["status"] == "True":
                            ready = True
                            break
                
                restarts = sum(
                    container.get("restartCount", 0) 
                    for container in pod_status.get("containerStatuses", [])
                )
                
                # Get container state details for better diagnosis
                container_issues = []
                for container in pod_status.get("containerStatuses", []):
                    state = container.get("state", {})
                    if "waiting" in state:
                        reason = state["waiting"].get("reason", "Unknown")
                        message = state["waiting"].get("message", "")
                        container_issues.append(f"{reason}: {message}")
                
                # AI-driven pod health assessment
                pod_health = {
                    "phase": pod_status.get("phase", "Unknown"),
                    "ready": ready,
                    "restarts": restarts,
                    "age": _calculate_pod_age(pod["metadata"].get("creationTimestamp")),
                    "ai_risk_score": _calculate_ai_risk_score(pod_status, restarts),
                    "container_issues": container_issues
                }
                
                analysis["pods"][pod_name] = pod_health
                
                if ready:
                    ready_pods += 1
                
                # AI Insights Generation
                if restarts > 0:
                    analysis["ai_insights"].append({
                        "type": "stability_concern",
                        "message": f"Pod {pod_name} has {restarts} restarts - investigating crash patterns",
                        "confidence": 0.9,
                        "impact": "medium"
                    })
                
                if pod_health["ai_risk_score"] > 70:
                    analysis["predictions"].append({
                        "type": "failure_prediction",
                        "message": f"Pod {pod_name} shows high risk indicators - potential failure in next 30min",
                        "probability": pod_health["ai_risk_score"] / 100,
                        "timeframe": "30 minutes"
                    })
            
            # Calculate overall health score
            if total_pods > 0:
                base_score = (ready_pods / total_pods) * 100
                # Adjust for AI risk factors
                risk_penalty = sum(pod["ai_risk_score"] for pod in analysis["pods"].values()) / len(analysis["pods"]) if analysis["pods"] else 0
                analysis["health_score"] = max(0, base_score - (risk_penalty * 0.3))
        
        # Correlate with Prometheus metrics for deeper insights
        _correlate_metrics_with_pods(analysis)
        
        # Generate AI-driven recommendations
        _generate_ai_recommendations(analysis)
        
        # Add traceability for CI/CD context
        analysis["traceability"].append({
            "source": "kubernetes_api",
            "timestamp": datetime.now().isoformat(),
            "pipeline_correlation": CI_PIPELINE_ID,
            "data_points": len(analysis["pods"])
        })
        
    except Exception as e:
        analysis["error"] = str(e)
        analysis["ai_insights"].append({
            "type": "system_error",
            "message": f"Failed to analyze system health: {e}",
            "confidence": 1.0,
            "impact": "high"
        })
    
    return analysis

@tool
def correlate_events_and_metrics() -> Dict[str, Any]:
    """
    AI-Powered Event Correlation
    Correlates events across metrics, logs, and infrastructure changes
    """
    correlation = {
        "timestamp": datetime.now().isoformat(),
        "correlations_found": [],
        "anomalies": [],
        "causal_chains": [],
        "confidence_scores": {}
    }
    
    try:
        # Get recent Kubernetes events
        events_cmd = ["kubectl", "get", "events", "-n", NAMESPACE, "--sort-by=.lastTimestamp", "-o", "json"]
        events_result = subprocess.run(events_cmd, capture_output=True, text=True, timeout=10)
        
        recent_events = []
        if events_result.returncode == 0:
            events_data = json.loads(events_result.stdout)
            # Get events from last 15 minutes
            cutoff_time = datetime.now() - timedelta(minutes=5)
            
            for event in events_data.get("items", []):
                event_time = datetime.fromisoformat(event["lastTimestamp"].replace("Z", "+00:00"))
                if event_time > cutoff_time:
                    recent_events.append({
                        "time": event["lastTimestamp"],
                        "type": event["type"],
                        "reason": event["reason"],
                        "message": event["message"],
                        "object": event["involvedObject"]["name"]
                    })
        
        # Correlate with Prometheus metrics
        metric_queries = {
            "error_rate": 'rate(http_requests_total{status=~"5.."}[5m])',
            "latency_p95": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
            "cpu_usage": f'avg(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}"}}[5m])) * 100',
            "memory_usage": f'avg(container_memory_usage_bytes{{namespace="{NAMESPACE}"}}) / 1024 / 1024'
        }
        
        current_metrics = {}
        for metric_name, query in metric_queries.items():
            try:
                response = requests.get(f"{PROM_URL}/api/v1/query", 
                                      params={"query": query}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data", {}).get("result"):
                        current_metrics[metric_name] = float(data["data"]["result"][0]["value"][1])
            except:
                continue
        
        # AI-driven correlation analysis
        _analyze_correlations(correlation, recent_events, current_metrics)
        
        # Generate causal chains
        _generate_causal_chains(correlation, recent_events, current_metrics)
        
    except Exception as e:
        correlation["error"] = str(e)
    
    return correlation

@tool
def predict_system_behavior() -> Dict[str, Any]:
    """
    Predictive Analytics for Proactive Insights
    Uses historical data to predict potential issues and capacity needs
    """
    predictions = {
        "timestamp": datetime.now().isoformat(),
        "predictions": [],
        "confidence_intervals": {},
        "recommended_actions": [],
        "time_to_action": {}
    }
    
    try:
        # Get historical metrics for trend analysis
        end_time = int(time.time())
        start_time = end_time - 3600  # Last hour
        
        trend_queries = {
            "cpu_trend": f'avg(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}"}}[5m]))',
            "memory_trend": f'avg(container_memory_usage_bytes{{namespace="{NAMESPACE}"}})',
            "error_trend": 'rate(http_requests_total{status=~"5.."}[5m])',
            "request_trend": 'rate(http_requests_total[5m])'
        }
        
        trends = {}
        for metric_name, query in trend_queries.items():
            try:
                response = requests.get(f"{PROM_URL}/api/v1/query_range", 
                                      params={
                                          "query": query,
                                          "start": start_time,
                                          "end": end_time,
                                          "step": "300s"  # 5-minute intervals
                                      }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data", {}).get("result"):
                        values = data["data"]["result"][0]["values"]
                        trends[metric_name] = [float(v[1]) for v in values]
            except:
                continue
        
        # AI-powered trend analysis and predictions
        for metric_name, values in trends.items():
            if len(values) >= 3:
                prediction = _analyze_trend_and_predict(metric_name, values)
                if prediction:
                    predictions["predictions"].append(prediction)
        
        # Generate proactive recommendations
        _generate_proactive_recommendations(predictions, trends)
        
    except Exception as e:
        predictions["error"] = str(e)
    
    return predictions

@tool
def explain_failure_with_context(failure_description: str = "auto-detect") -> Dict[str, Any]:
    """
    AI-Powered Failure Explanation
    Automatically explains failures with full context and root cause analysis
    """
    explanation = {
        "timestamp": datetime.now().isoformat(),
        "failure_context": {},
        "root_cause_analysis": [],
        "contributing_factors": [],
        "resolution_steps": [],
        "prevention_measures": [],
        "confidence_score": 0.0
    }
    
    try:
        if failure_description == "auto-detect":
            # Auto-detect current failures
            health = analyze_system_health()
            
            failures = []
            for pod_name, pod_info in health.get("pods", {}).items():
                if not pod_info["ready"] or pod_info["restarts"] > 0:
                    failures.append(f"Pod {pod_name}: ready={pod_info['ready']}, restarts={pod_info['restarts']}")
            
            if not failures:
                # Check for metric-based failures
                correlation = correlate_events_and_metrics()
                if correlation.get("anomalies"):
                    failures = [anomaly["description"] for anomaly in correlation["anomalies"]]
            
            failure_description = "; ".join(failures) if failures else "No active failures detected"
        
        explanation["failure_context"]["description"] = failure_description
        explanation["failure_context"]["pipeline_id"] = CI_PIPELINE_ID
        explanation["failure_context"]["environment"] = CI_ENVIRONMENT
        
        # Get comprehensive context
        system_health = analyze_system_health()
        event_correlation = correlate_events_and_metrics()
        
        # AI-driven root cause analysis
        _perform_root_cause_analysis(explanation, system_health, event_correlation)
        
        # Generate resolution steps
        _generate_resolution_steps(explanation, failure_description)
        
        # Calculate confidence score
        explanation["confidence_score"] = _calculate_explanation_confidence(explanation)
        
    except Exception as e:
        explanation["error"] = str(e)
    
    return explanation

@tool
def send_cicd_notification(message: str, severity: str = "info", include_context: bool = True) -> str:
    """
    Send CI/CD-focused notifications to Telegram with pipeline context
    """
    if not TELEGRAM_ENABLED:
        return "❌ Telegram notifications not configured"
    
    try:
        # Severity emojis
        emoji_map = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️",
            "success": "✅",
            "deployment": "🚀",
            "rollback": "🔄"
        }
        
        emoji = emoji_map.get(severity.lower(), "🔔")
        
        # Build notification message
        notification = f"{emoji} *AI Observability Alert*\n\n"
        
        if include_context:
            notification += f"*Pipeline:* `{CI_PIPELINE_ID}`\n"
            notification += f"*Environment:* `{CI_ENVIRONMENT}`\n"
            notification += f"*Namespace:* `{NAMESPACE}`\n"
            notification += f"*Commit:* `{CI_COMMIT_SHA[:8]}`\n"
            notification += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        
        notification += f"*Alert:*\n{message}\n\n"
        
        # Add quick actions
        notification += "*Quick Actions:*\n"
        notification += f"• [View Grafana]({GRAFANA_URL})\n"
        notification += f"• [Check Prometheus]({PROM_URL})\n"
        notification += "• Run: `kubectl get pods -n " + NAMESPACE + "`"
        
        # Send to Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": notification,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        response = requests.post(telegram_url, json=payload, timeout=10)
        response.raise_for_status()
        
        return f"✅ CI/CD notification sent successfully (severity: {severity})"
        
    except Exception as e:
        return f"❌ Failed to send notification: {str(e)}"

@tool
def simulate_chaos_scenario(scenario_type: str = "latency") -> Dict[str, Any]:
    """
    Simulate chaos scenarios for testing system resilience
    Helps validate AI observability capabilities
    """
    simulation = {
        "timestamp": datetime.now().isoformat(),
        "scenario": scenario_type,
        "expected_impacts": [],
        "monitoring_points": [],
        "success_criteria": [],
        "ai_predictions": []
    }
    
    scenarios = {
        "latency": {
            "description": "Inject network latency to test response time monitoring",
            "expected_impacts": ["Increased P95/P99 latency", "Potential timeout errors"],
            "monitoring_points": ["http_request_duration_seconds", "error rates"],
            "success_criteria": ["AI detects latency spike", "Alerts triggered within 2 minutes"]
        },
        "cpu_spike": {
            "description": "Simulate CPU pressure to test resource monitoring",
            "expected_impacts": ["High CPU utilization", "Potential pod throttling"],
            "monitoring_points": ["container_cpu_usage_seconds_total", "pod restarts"],
            "success_criteria": ["AI predicts resource exhaustion", "Auto-scaling triggered"]
        },
        "memory_leak": {
            "description": "Simulate memory leak to test predictive capabilities",
            "expected_impacts": ["Gradual memory increase", "OOMKilled events"],
            "monitoring_points": ["container_memory_usage_bytes", "pod events"],
            "success_criteria": ["AI predicts OOM before it happens", "Proactive scaling"]
        },
        "network_partition": {
            "description": "Simulate network issues to test service mesh monitoring",
            "expected_impacts": ["Service connectivity issues", "Circuit breaker activation"],
            "monitoring_points": ["service mesh metrics", "connection errors"],
            "success_criteria": ["AI correlates network and application metrics"]
        }
    }
    
    if scenario_type in scenarios:
        scenario_config = scenarios[scenario_type]
        simulation.update(scenario_config)
        
        # Generate AI predictions for this scenario
        simulation["ai_predictions"] = [
            f"Expected detection time: 30-60 seconds",
            f"Predicted impact severity: {_predict_scenario_severity(scenario_type)}",
            f"Recommended monitoring focus: {', '.join(scenario_config['monitoring_points'])}"
        ]
    
    return simulation

# ---- Helper Functions ----

def _calculate_pod_age(creation_timestamp: str) -> int:
    """Calculate pod age in minutes"""
    if not creation_timestamp:
        return 0
    try:
        created = datetime.fromisoformat(creation_timestamp.replace("Z", "+00:00"))
        age = datetime.now(created.tzinfo) - created
        return int(age.total_seconds() / 60)
    except:
        return 0

def _calculate_ai_risk_score(pod_status: Dict, restarts: int) -> float:
    """Calculate AI-driven risk score for a pod"""
    risk_score = 0.0
    
    # Base risk from restarts
    risk_score += min(restarts * 20, 60)  # Max 60 points from restarts
    
    # Risk from pod phase
    phase = pod_status.get("phase", "Unknown")
    if phase != "Running":
        risk_score += 40
    
    # Risk from container states
    for container in pod_status.get("containerStatuses", []):
        if not container.get("ready", False):
            risk_score += 20
        
        state = container.get("state", {})
        if "waiting" in state:
            reason = state["waiting"].get("reason", "")
            if reason in ["CrashLoopBackOff", "ImagePullBackOff"]:
                risk_score += 30
    
    return min(risk_score, 100.0)

def _correlate_metrics_with_pods(analysis: Dict):
    """Correlate Prometheus metrics with pod health"""
    try:
        # Get key metrics
        metrics_queries = {
            "error_rate": 'rate(http_requests_total{status=~"5.."}[5m])',
            "cpu_usage": f'avg(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}"}}[5m])) * 100'
        }
        
        for metric_name, query in metrics_queries.items():
            try:
                response = requests.get(f"{PROM_URL}/api/v1/query", 
                                      params={"query": query}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data", {}).get("result"):
                        value = float(data["data"]["result"][0]["value"][1])
                        
                        # Generate correlations
                        if metric_name == "error_rate" and value > 0.01:
                            analysis["correlations"].append({
                                "type": "metric_pod_correlation",
                                "message": f"High error rate ({value:.3f}/sec) may correlate with pod issues",
                                "confidence": 0.8
                            })
            except:
                continue
    except:
        pass

def _generate_ai_recommendations(analysis: Dict):
    """Generate AI-driven recommendations"""
    health_score = analysis["health_score"]
    
    if health_score < 50:
        analysis["recommendations"].append({
            "priority": "critical",
            "action": "immediate_investigation",
            "description": "Multiple pods failing - investigate cluster resources and recent deployments",
            "estimated_impact": "high"
        })
    elif health_score < 80:
        analysis["recommendations"].append({
            "priority": "medium",
            "action": "proactive_monitoring",
            "description": "Some pods showing issues - increase monitoring frequency",
            "estimated_impact": "medium"
        })
    
    # Add predictive recommendations
    if analysis["predictions"]:
        analysis["recommendations"].append({
            "priority": "proactive",
            "action": "preventive_scaling",
            "description": "AI predicts potential issues - consider preemptive scaling",
            "estimated_impact": "low"
        })

def _analyze_correlations(correlation: Dict, events: List, metrics: Dict):
    """Analyze correlations between events and metrics"""
    # Look for patterns
    error_events = [e for e in events if e["type"] == "Warning"]
    
    if error_events and metrics.get("error_rate", 0) > 0.01:
        correlation["correlations_found"].append({
            "type": "event_metric_correlation",
            "description": f"Warning events correlate with high error rate ({metrics['error_rate']:.3f}/sec)",
            "confidence": 0.9,
            "events_count": len(error_events)
        })

def _generate_causal_chains(correlation: Dict, events: List, metrics: Dict):
    """Generate causal chains for root cause analysis"""
    # Simple causal chain example
    if events and metrics:
        correlation["causal_chains"].append({
            "chain": "Deployment → Pod Restart → Service Disruption → Error Rate Increase",
            "probability": 0.75,
            "evidence": f"{len(events)} events, error rate: {metrics.get('error_rate', 0):.3f}/sec"
        })

def _analyze_trend_and_predict(metric_name: str, values: List[float]) -> Optional[Dict]:
    """Analyze trend and make predictions"""
    if len(values) < 3:
        return None
    
    # Simple trend analysis
    recent_avg = sum(values[-3:]) / 3
    older_avg = sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else recent_avg
    
    trend_change = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    
    if abs(trend_change) > 20:  # Significant change
        direction = "increasing" if trend_change > 0 else "decreasing"
        return {
            "metric": metric_name,
            "trend": direction,
            "change_percent": abs(trend_change),
            "prediction": f"{metric_name} trending {direction} by {abs(trend_change):.1f}%",
            "confidence": min(0.9, abs(trend_change) / 50)
        }
    
    return None

def _generate_proactive_recommendations(predictions: Dict, trends: Dict):
    """Generate proactive recommendations based on predictions"""
    for prediction in predictions["predictions"]:
        if "cpu" in prediction["metric"] and prediction["trend"] == "increasing":
            predictions["recommended_actions"].append({
                "action": "scale_up_cpu",
                "description": "CPU usage trending up - consider horizontal pod autoscaling",
                "urgency": "medium",
                "time_to_implement": "5 minutes"
            })
        elif "memory" in prediction["metric"] and prediction["trend"] == "increasing":
            predictions["recommended_actions"].append({
                "action": "investigate_memory_leak",
                "description": "Memory usage increasing - check for memory leaks",
                "urgency": "high",
                "time_to_implement": "immediate"
            })

def _perform_root_cause_analysis(explanation: Dict, health: Dict, correlation: Dict):
    """Perform AI-driven root cause analysis"""
    # Analyze patterns
    if health.get("ai_insights"):
        for insight in health["ai_insights"]:
            if insight["type"] == "stability_concern":
                explanation["root_cause_analysis"].append({
                    "cause": "pod_instability",
                    "evidence": insight["message"],
                    "confidence": insight["confidence"]
                })
    
    if correlation.get("correlations_found"):
        for corr in correlation["correlations_found"]:
            explanation["contributing_factors"].append({
                "factor": "metric_event_correlation",
                "description": corr["description"],
                "confidence": corr["confidence"]
            })

def _generate_resolution_steps(explanation: Dict, failure_description: str):
    """Generate step-by-step resolution"""
    explanation["resolution_steps"] = [
        {
            "step": 1,
            "action": "immediate_assessment",
            "description": "Check pod status and recent events",
            "command": f"kubectl get pods -n {NAMESPACE} && kubectl get events -n {NAMESPACE}"
        },
        {
            "step": 2,
            "action": "log_analysis",
            "description": "Examine pod logs for error patterns",
            "command": f"kubectl logs -n {NAMESPACE} --tail=100"
        },
        {
            "step": 3,
            "action": "metric_correlation",
            "description": "Check Prometheus metrics for anomalies",
            "command": "Query error rates and resource utilization"
        }
    ]

def _calculate_explanation_confidence(explanation: Dict) -> float:
    """Calculate confidence score for the explanation"""
    confidence_factors = []
    
    if explanation.get("root_cause_analysis"):
        avg_confidence = sum(rca["confidence"] for rca in explanation["root_cause_analysis"]) / len(explanation["root_cause_analysis"])
        confidence_factors.append(avg_confidence)
    
    if explanation.get("contributing_factors"):
        avg_confidence = sum(cf["confidence"] for cf in explanation["contributing_factors"]) / len(explanation["contributing_factors"])
        confidence_factors.append(avg_confidence)
    
    return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

def _predict_scenario_severity(scenario_type: str) -> str:
    """Predict severity of chaos scenario"""
    severity_map = {
        "latency": "medium",
        "cpu_spike": "high", 
        "memory_leak": "critical",
        "network_partition": "high"
    }
    return severity_map.get(scenario_type, "medium")

def _generate_simulation_health_analysis(analysis: Dict) -> Dict[str, Any]:
    """Generate simulated health analysis for testing environments"""
    import random
    
    # Simulate realistic health data
    base_health = random.randint(70, 95)
    num_pods = random.randint(3, 8)
    
    # Generate simulated pods
    for i in range(num_pods):
        pod_name = f"app-{random.choice(['frontend', 'backend', 'api', 'worker'])}-{random.randint(1000, 9999)}"
        
        # Most pods should be healthy in simulation
        is_ready = random.random() > 0.1  # 90% success rate
        restarts = random.randint(0, 2) if not is_ready else 0
        
        analysis["pods"][pod_name] = {
            "phase": "Running" if is_ready else random.choice(["Pending", "Failed"]),
            "ready": is_ready,
            "restarts": restarts,
            "age": random.randint(10, 1440),  # 10 minutes to 24 hours
            "ai_risk_score": random.randint(0, 30) if is_ready else random.randint(40, 80),
            "container_issues": [] if is_ready else ["ImagePullBackOff: Failed to pull image"]
        }
    
    # Calculate health score
    ready_pods = sum(1 for pod in analysis["pods"].values() if pod["ready"])
    analysis["health_score"] = int((ready_pods / num_pods) * 100) if num_pods > 0 else 100
    
    # Add AI insights for simulation
    analysis["ai_insights"].extend([
        {
            "type": "simulation_mode",
            "message": "Running in simulation mode - data is generated for demonstration",
            "confidence": 1.0,
            "impact": "info"
        },
        {
            "type": "environment_detection",
            "message": f"Environment auto-detected as {env_config.env_type.value}",
            "confidence": 1.0,
            "impact": "info"
        }
    ])
    
    # Add some realistic predictions
    if analysis["health_score"] < 90:
        analysis["predictions"].append({
            "type": "performance_trend",
            "message": "System performance trending stable with minor fluctuations expected",
            "probability": 0.75,
            "timeframe": "next 30 minutes"
        })
    
    # Add recommendations
    analysis["recommendations"].extend([
        {
            "priority": "info",
            "action": "simulation_validation",
            "description": "Simulation mode is perfect for testing AI observability without infrastructure",
            "estimated_impact": "educational"
        },
        {
            "priority": "medium",
            "action": "setup_real_monitoring",
            "description": "Consider setting up real monitoring endpoints for production use",
            "estimated_impact": "high"
        }
    ])
    
    # Add traceability
    analysis["traceability"].append({
        "source": "simulation_engine",
        "timestamp": datetime.now().isoformat(),
        "pipeline_correlation": CI_PIPELINE_ID,
        "data_points": len(analysis["pods"]),
        "simulation_seed": random.randint(1000, 9999)
    })
    
    return analysis

def _generate_external_health_analysis(analysis: Dict) -> Dict[str, Any]:
    """Generate health analysis using external monitoring endpoints"""
    
    # Try to get data from external Prometheus if available
    if PROM_URL and PROM_URL != "http://mock-prometheus":
        try:
            # Query external Prometheus for basic metrics
            queries = {
                "up_targets": "up",
                "error_rate": 'rate(http_requests_total{status=~"5.."}[5m])',
                "response_time": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'
            }
            
            external_metrics = {}
            for metric_name, query in queries.items():
                try:
                    response = requests.get(f"{PROM_URL}/api/v1/query", 
                                          params={"query": query}, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("data", {}).get("result"):
                            external_metrics[metric_name] = data["data"]["result"]
                except Exception as e:
                    print(f"Failed to query {metric_name}: {e}")
            
            # Analyze external metrics
            if external_metrics:
                up_targets = len(external_metrics.get("up_targets", []))
                analysis["health_score"] = min(100, max(0, up_targets * 20))  # Rough estimate
                
                analysis["ai_insights"].append({
                    "type": "external_monitoring",
                    "message": f"Analysis based on external Prometheus with {up_targets} targets",
                    "confidence": 0.8,
                    "impact": "medium"
                })
        
        except Exception as e:
            print(f"Failed to connect to external Prometheus: {e}")
    
    # Fallback to basic analysis
    if not analysis.get("ai_insights"):
        analysis["health_score"] = 75  # Conservative estimate
        analysis["ai_insights"].append({
            "type": "limited_visibility",
            "message": "Limited monitoring data available - consider enabling Kubernetes access or external monitoring",
            "confidence": 0.6,
            "impact": "medium"
        })
    
    # Add environment-specific recommendations
    if env_config.env_type == EnvironmentType.GITHUB_ACTIONS:
        analysis["recommendations"].append({
            "priority": "medium",
            "action": "enable_cluster_access",
            "description": "Configure Kubernetes access in GitHub Actions for deeper observability",
            "estimated_impact": "high"
        })
    
    analysis["traceability"].append({
        "source": "external_monitoring",
        "timestamp": datetime.now().isoformat(),
        "pipeline_correlation": CI_PIPELINE_ID,
        "monitoring_endpoints": len([url for url in [PROM_URL, GRAFANA_URL] if url])
    })
    
    return analysis

# ---- Dynamic System Prompt Based on Environment ----
def _generate_system_prompt() -> str:
    """Generate dynamic system prompt based on detected environment"""
    
    base_context = f"""
You are an INTELLIGENT AI Observability Agent with adaptive capabilities.

**Environment Context:**
- Type: {env_config.env_type.value}
- Pipeline: {CI_PIPELINE_ID} | Environment: {CI_ENVIRONMENT} | Namespace: {NAMESPACE}
- Kubernetes Available: {env_config.kubernetes_available}
- Cloud Provider: {env_config.cloud_provider or 'None'}
- Auth Method: {env_config.auth_method}

**Available Capabilities:**
"""
    
    # Add capability-specific context
    capabilities_text = ""
    for capability, enabled in env_config.capabilities.items():
        status = "✅" if enabled else "❌"
        capabilities_text += f"- {capability}: {status}\n"
    
    # Environment-specific rules
    if env_config.env_type == EnvironmentType.SIMULATION:
        rules = """
**SIMULATION MODE RULES:**
1. ALWAYS mention this is simulation mode
2. Focus on demonstrating AI capabilities
3. Provide educational insights about observability
4. Suggest real-world setup steps
5. Maximum 200 words total
"""
        response_format = """
**Response Format:**
```
🎭 SIMULATION MODE ANALYSIS

**Simulated Health:** [Score]/100
**AI Insights:** [Key observations from simulated data]
**Learning Points:** [What this demonstrates]
**Next Steps:** [How to implement in real environment]
```
"""
    
    elif not env_config.kubernetes_available:
        rules = """
**EXTERNAL MONITORING RULES:**
1. Work with available external endpoints
2. Acknowledge limited visibility
3. Provide setup recommendations
4. Focus on available metrics
5. Maximum 150 words total
"""
        response_format = """
**Response Format:**
```
📊 EXTERNAL MONITORING ANALYSIS

**Health Score:** [X]/100 (based on available data)
**Data Sources:** [What monitoring is available]
**Recommendations:** [How to improve observability]
**Action:** [Whether deployment should proceed]
```
"""
    
    else:
        rules = f"""
**KUBERNETES MONITORING RULES:**
1. ALWAYS use analyze_system_health() first
2. If ANY pod is not ready, this is CRITICAL - use explain_failure_with_context()
3. For critical issues, ALWAYS use send_cicd_notification() 
4. Give EXACT kubectl commands, not generic advice
5. Maximum 150 words total
"""
        response_format = f"""
**Response Format:**
For Problems:
```
🚨 DEPLOYMENT BLOCKED

**Problem:** [Exact issue - e.g., "Pod blackjack-app-xxx has ImagePullBackOff"]
**Root Cause:** [Technical reason - e.g., "Container image cannot be pulled"]
**Impact:** [e.g., "33% capacity reduction, service degraded"]

**Immediate Actions:**
1. kubectl describe pod [POD_NAME] -n {NAMESPACE}
2. [Specific fix - e.g., "Fix image tag in deployment"]
3. kubectl get events -n {NAMESPACE} --sort-by=.lastTimestamp

**Telegram Alert:** ✅ Sent
```

For Healthy Systems:
```
✅ DEPLOYMENT APPROVED

**Status:** All pods running normally
**Health Score:** [X]/100
**Action:** Deployment can proceed safely
```
"""
    
    return base_context + capabilities_text + rules + response_format + """

BE PRECISE. Adapt your analysis to the available environment capabilities. This is the future of observability - intelligent, predictive, and context-aware!
"""

SYSTEM_PROMPT = _generate_system_prompt()

# Create the AI-Driven Observability Agent
if model is not None:
    agent = Agent(
        model=model,
        tools=[
            analyze_system_health,
            correlate_events_and_metrics, 
            predict_system_behavior,
            explain_failure_with_context,
            send_cicd_notification,
            simulate_chaos_scenario
        ],
        system_prompt=SYSTEM_PROMPT
    )
else:
    # In simulation mode, we'll create a mock agent
    agent = None

async def main():
    """
    Main execution - Demonstrate AI-Driven Observability
    """
    print("🤖 AI-Driven Observability Agent")
    print("AWS re:Invent 2025 - Supercharge DevOps with AI-driven observability")
    print("=" * 80)
    print(f"Pipeline: {CI_PIPELINE_ID} | Environment: {CI_ENVIRONMENT} | Namespace: {NAMESPACE}")
    print("=" * 80)
    
    # Check if blocking mode is enabled
    blocking_mode = os.getenv("BLOCKING_MODE", "true").lower() == "true"
    print(f"🔒 Blocking Mode: {'Enabled' if blocking_mode else 'Disabled'}")
    
    # Get specific pod status first
    health_analysis = analyze_system_health()
    
    # Build specific query based on actual issues found
    pod_issues = []
    for pod_name, pod_info in health_analysis.get("pods", {}).items():
        if not pod_info.get("ready", False):
            issues = pod_info.get("container_issues", [])
            if issues:
                pod_issues.append(f"Pod {pod_name}: {', '.join(issues)}")
            else:
                pod_issues.append(f"Pod {pod_name}: {pod_info.get('phase', 'Unknown')} state")
    
    if pod_issues:
        query = f"""
        CRITICAL ISSUES DETECTED in {CI_ENVIRONMENT}:
        {chr(10).join(pod_issues)}
        
        Provide EXACTLY this format (max 150 words):
        
        🚨 DEPLOYMENT BLOCKED
        
        **Problem:** [One specific sentence about the main issue]
        **Root Cause:** [Most likely technical cause]
        **Impact:** [Business impact in one sentence]
        
        **Immediate Actions:**
        1. [Exact kubectl command to investigate]
        2. [Specific fix action]
        3. [Verification step]
        
        **Telegram Alert:** Send critical notification about this blocking issue.
        
        Use analyze_system_health(), explain_failure_with_context(), and send_cicd_notification().
        """
    else:
        query = f"""
        System appears healthy in {CI_ENVIRONMENT}. 
        
        Provide brief confirmation:
        ✅ DEPLOYMENT APPROVED
        **Status:** All pods running normally
        **Health Score:** [X]/100
        **Action:** Deployment can proceed
        
        Use analyze_system_health() to confirm.
        """
    
    exit_code = 0
    
    try:
        print("🔍 Analyzing system with AI-driven observability...")
        print("-" * 50)
        
        # First, get system health to determine if we should fail
        health_analysis = analyze_system_health()
        health_score = health_analysis.get("health_score", 0)
        
        # Check for critical issues with detailed status
        critical_issues = 0
        critical_details = []
        
        # In simulation mode, provide direct output without AI agent
        if simulation_mode or agent is None:
            print("🎭 SIMULATION MODE ANALYSIS")
            print("")
            print(f"**Simulated Health:** {health_score}/100")
            print(f"**AI Insights:** {len(health_analysis.get('ai_insights', []))} insights generated")
            print(f"**Learning Points:** This demonstrates AI observability capabilities without infrastructure")
            print(f"**Next Steps:** Configure AWS credentials for real AI analysis")
            print("")
            
            # Show some insights
            for insight in health_analysis.get("ai_insights", [])[:3]:
                print(f"💡 {insight.get('message', 'AI insight generated')}")
            
            print(f"\n📊 System Health Score: {health_score}/100")
            print(f"🚨 Critical Issues Found: {critical_issues}")
            
            if critical_issues > 0:
                print("❌ SIMULATION: Issues detected - would block in real mode")
                exit_code = 1
            else:
                print("✅ SIMULATION: System health acceptable")
                exit_code = 0
                
            return exit_code
        
        for pod_name, pod_info in health_analysis.get("pods", {}).items():
            if not pod_info.get("ready", False):
                critical_issues += 1
                status = health_analysis.get("pods", {}).get(pod_name, {}).get("phase", "Unknown")
                critical_details.append(f"Pod {pod_name}: {status}")
                print(f"🚨 CRITICAL: Pod {pod_name} is not ready (Status: {status})")
            
            if pod_info.get("ai_risk_score", 0) > 80:
                critical_issues += 1
                risk_score = pod_info.get("ai_risk_score", 0)
                critical_details.append(f"Pod {pod_name}: High risk ({risk_score})")
                print(f"🚨 CRITICAL: Pod {pod_name} has high AI risk score: {risk_score}")
        
        # Print summary of critical issues
        if critical_details:
            print(f"📋 Critical Issues Summary:")
            for detail in critical_details:
                print(f"   - {detail}")
        
        # Run full AI analysis
        result = await agent.invoke_async(query)
        
        # Handle different response types
        if hasattr(result, 'content'):
            print(result.content)
        elif hasattr(result, 'text'):
            print(result.text)
        elif isinstance(result, str):
            print(result)
        else:
            print(f"AI Analysis Complete: {result}")
        
        # Determine exit code based on analysis
        print(f"\n📊 System Health Score: {health_score}/100")
        print(f"🚨 Critical Issues Found: {critical_issues}")
        
        if blocking_mode:
            if critical_issues > 0:
                print("❌ CRITICAL ISSUES DETECTED - Pipeline should be blocked")
                exit_code = 1
            elif health_score < 70:
                print("⚠️  HEALTH SCORE BELOW THRESHOLD - Pipeline should be blocked")
                exit_code = 1
            else:
                print("✅ System health acceptable - Pipeline can continue")
        else:
            print("ℹ️  Non-blocking mode - Pipeline continues regardless of issues")
            
        print("\n" + "=" * 80)
        print("🎯 AI-Driven Observability Demo Complete!")
        print("This demonstrates how Generative AI transforms DevOps and SRE practices")
        print("=" * 80)
            
    except Exception as e:
        print(f"❌ Error during AI analysis: {e}")
        import traceback
        traceback.print_exc()
        
        # Send error notification only if we have a real agent
        if TELEGRAM_ENABLED and agent is not None:
            try:
                error_msg = f"AI Observability Agent encountered an error: {str(e)}"
                await agent.invoke_async(f'send_cicd_notification("{error_msg}", "critical")')
            except:
                print("⚠️  Could not send error notification")
        
        exit_code = 2  # Error exit code
    
    # Exit with appropriate code
    import sys
    sys.exit(exit_code)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())