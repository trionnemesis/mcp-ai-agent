"""
Intelligent System Monitoring Assistant
Provides automated monitoring with AI-driven analysis and alerting
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil
from pydantic import BaseModel

from .base_agent import BaseMCPAgent, AIResponse
from ..utils.config import Config


class SystemMetrics(BaseModel):
    """System metrics data model"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: Optional[List[float]] = None


class AlertRule(BaseModel):
    """Alert rule definition"""
    name: str
    metric: str
    threshold: float
    operator: str  # '>', '<', '>=', '<='
    duration: int  # seconds
    severity: str  # 'info', 'warning', 'critical'


class Alert(BaseModel):
    """Alert data model"""
    rule_name: str
    message: str
    severity: str
    timestamp: datetime
    current_value: float
    threshold: float


class MonitoringAgent(BaseMCPAgent):
    """
    Intelligent System Monitoring Assistant

    Features:
    - Real-time system monitoring
    - AI-driven anomaly detection
    - Predictive trend analysis
    - Automated alerting
    - Performance optimization suggestions
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self.metrics_history: List[SystemMetrics] = []
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: List[Alert] = []
        self.monitoring_active = False
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default monitoring rules"""
        self.alert_rules = [
            AlertRule(
                name="high_cpu_usage",
                metric="cpu_percent",
                threshold=self.config.cpu_threshold,
                operator=">=",
                duration=60,
                severity="warning"
            ),
            AlertRule(
                name="critical_cpu_usage",
                metric="cpu_percent",
                threshold=95.0,
                operator=">=",
                duration=30,
                severity="critical"
            ),
            AlertRule(
                name="high_memory_usage",
                metric="memory_percent",
                threshold=self.config.memory_threshold,
                operator=">=",
                duration=120,
                severity="warning"
            ),
            AlertRule(
                name="critical_memory_usage",
                metric="memory_percent",
                threshold=95.0,
                operator=">=",
                duration=60,
                severity="critical"
            ),
            AlertRule(
                name="high_disk_usage",
                metric="disk_percent",
                threshold=self.config.disk_threshold,
                operator=">=",
                duration=300,
                severity="warning"
            ),
            AlertRule(
                name="critical_disk_usage",
                metric="disk_percent",
                threshold=98.0,
                operator=">=",
                duration=60,
                severity="critical"
            )
        ]

    async def run(self) -> None:
        """Main monitoring loop"""
        await self.initialize()

        self.logger.info("Starting intelligent system monitoring...")
        self.monitoring_active = True

        # Start monitoring tasks
        monitor_task = asyncio.create_task(self._monitoring_loop())
        analysis_task = asyncio.create_task(self._analysis_loop())
        alert_task = asyncio.create_task(self._alert_loop())

        try:
            await asyncio.gather(monitor_task, analysis_task, alert_task)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.monitoring_active = False
            await self.cleanup()

    async def _monitoring_loop(self) -> None:
        """Main monitoring data collection loop"""
        while self.monitoring_active:
            try:
                metrics = await self._collect_system_metrics()
                self.metrics_history.append(metrics)

                # Keep only last 1000 metrics (approximately 8 hours at 30s intervals)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]

                await asyncio.sleep(self.config.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.monitoring_interval)

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk usage for root partition
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100

        # Network I/O
        network_io = psutil.net_io_counters()._asdict()

        # Process count
        process_count = len(psutil.pids())

        # Load average (if available)
        load_average = None
        try:
            if hasattr(psutil, 'getloadavg'):
                load_average = list(psutil.getloadavg())
        except (AttributeError, OSError):
            pass

        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            process_count=process_count,
            load_average=load_average
        )

    async def _analysis_loop(self) -> None:
        """AI-driven analysis loop"""
        while self.monitoring_active:
            try:
                if len(self.metrics_history) >= 10:  # Need at least 10 data points
                    await self._perform_trend_analysis()
                    await self._detect_anomalies()

                # Run analysis every 5 minutes
                await asyncio.sleep(300)

            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(300)

    async def _perform_trend_analysis(self) -> None:
        """Perform AI-driven trend analysis"""
        try:
            # Get last 30 data points (15 minutes of data)
            recent_metrics = self.metrics_history[-30:] if len(self.metrics_history) >= 30 else self.metrics_history

            # Prepare data for AI analysis
            metrics_data = {
                "cpu_trend": [m.cpu_percent for m in recent_metrics],
                "memory_trend": [m.memory_percent for m in recent_metrics],
                "disk_trend": [m.disk_percent for m in recent_metrics],
                "timestamps": [m.timestamp.isoformat() for m in recent_metrics]
            }

            # AI analysis prompt
            analysis_prompt = f"""
            Analyze the following system metrics trends and provide insights:

            {json.dumps(metrics_data, indent=2)}

            Please provide:
            1. Trend analysis (increasing, decreasing, stable)
            2. Potential issues or concerns
            3. Optimization recommendations
            4. Predicted values for next 30 minutes

            Respond in JSON format:
            {{
                "trends": {{
                    "cpu": "trend_description",
                    "memory": "trend_description",
                    "disk": "trend_description"
                }},
                "concerns": ["list", "of", "concerns"],
                "recommendations": ["list", "of", "recommendations"],
                "predictions": {{
                    "cpu_next_30min": predicted_value,
                    "memory_next_30min": predicted_value
                }}
            }}
            """

            response = await self._generate_response(analysis_prompt)
            analysis_result = self._parse_ai_response(response)

            self.logger.info(f"Trend analysis: {analysis_result.content}")

        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")

    async def _detect_anomalies(self) -> None:
        """AI-driven anomaly detection"""
        try:
            if len(self.metrics_history) < 20:
                return

            # Get baseline (last 50 metrics if available)
            baseline_size = min(50, len(self.metrics_history) - 10)
            baseline_metrics = self.metrics_history[-baseline_size-10:-10]
            current_metrics = self.metrics_history[-10:]

            # Calculate baseline statistics
            baseline_cpu = [m.cpu_percent for m in baseline_metrics]
            baseline_memory = [m.memory_percent for m in baseline_metrics]

            current_cpu = [m.cpu_percent for m in current_metrics]
            current_memory = [m.memory_percent for m in current_metrics]

            # Prepare anomaly detection prompt
            anomaly_prompt = f"""
            Detect anomalies in system metrics:

            Baseline CPU usage (last {len(baseline_cpu)} samples): {baseline_cpu}
            Current CPU usage (last 10 samples): {current_cpu}

            Baseline Memory usage (last {len(baseline_memory)} samples): {baseline_memory}
            Current Memory usage (last 10 samples): {current_memory}

            Analyze if current metrics show anomalous behavior compared to baseline.
            Consider patterns, sudden spikes, unusual drops, or consistency changes.

            Respond in JSON format:
            {{
                "anomalies_detected": true/false,
                "anomaly_details": [
                    {{
                        "metric": "cpu/memory",
                        "type": "spike/drop/pattern_change",
                        "severity": "low/medium/high",
                        "description": "detailed_description"
                    }}
                ],
                "recommended_actions": ["list", "of", "actions"]
            }}
            """

            response = await self._generate_response(anomaly_prompt)
            anomaly_result = self._parse_ai_response(response)

            if "anomalies_detected" in anomaly_result.content:
                self.logger.warning(f"Anomalies detected: {anomaly_result.content}")

        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {e}")

    async def _alert_loop(self) -> None:
        """Alert evaluation and notification loop"""
        while self.monitoring_active:
            try:
                if self.metrics_history:
                    await self._evaluate_alert_rules()

                # Check alerts every 30 seconds
                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Error in alert loop: {e}")
                await asyncio.sleep(30)

    async def _evaluate_alert_rules(self) -> None:
        """Evaluate alert rules against current metrics"""
        if not self.metrics_history:
            return

        current_metrics = self.metrics_history[-1]

        for rule in self.alert_rules:
            try:
                # Get metric value
                metric_value = getattr(current_metrics, rule.metric, None)
                if metric_value is None:
                    continue

                # Evaluate condition
                triggered = self._evaluate_condition(metric_value, rule.threshold, rule.operator)

                if triggered:
                    # Check if alert should be fired (consider duration)
                    if await self._should_fire_alert(rule, metric_value):
                        alert = Alert(
                            rule_name=rule.name,
                            message=f"{rule.metric} is {metric_value:.1f}% (threshold: {rule.threshold}%)",
                            severity=rule.severity,
                            timestamp=datetime.now(),
                            current_value=metric_value,
                            threshold=rule.threshold
                        )

                        await self._fire_alert(alert)

            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.name}: {e}")

    def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate alert condition"""
        if operator == ">=":
            return value >= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "<":
            return value < threshold
        return False

    async def _should_fire_alert(self, rule: AlertRule, current_value: float) -> bool:
        """Check if alert should be fired based on duration"""
        # Simple implementation - check if condition persisted for rule duration
        duration_samples = rule.duration // self.config.monitoring_interval

        if len(self.metrics_history) < duration_samples:
            return False

        # Check if condition was true for the required duration
        recent_metrics = self.metrics_history[-duration_samples:]

        for metrics in recent_metrics:
            metric_value = getattr(metrics, rule.metric, None)
            if metric_value is None:
                return False

            if not self._evaluate_condition(metric_value, rule.threshold, rule.operator):
                return False

        return True

    async def _fire_alert(self, alert: Alert) -> None:
        """Fire an alert"""
        # Check if alert is already active to avoid spam
        existing_alert = next(
            (a for a in self.active_alerts if a.rule_name == alert.rule_name),
            None
        )

        if existing_alert:
            # Update existing alert
            existing_alert.current_value = alert.current_value
            existing_alert.timestamp = alert.timestamp
            return

        # Add new alert
        self.active_alerts.append(alert)

        # Log alert
        self.logger.warning(f"ALERT [{alert.severity.upper()}]: {alert.message}")

        # AI-driven alert analysis and recommendations
        await self._analyze_alert(alert)

        # Keep only last 100 alerts
        if len(self.active_alerts) > 100:
            self.active_alerts = self.active_alerts[-100:]

    async def _analyze_alert(self, alert: Alert) -> None:
        """AI analysis of alert with recommendations"""
        try:
            # Get recent metrics for context
            recent_metrics = self.metrics_history[-20:] if len(self.metrics_history) >= 20 else self.metrics_history

            analysis_prompt = f"""
            System alert triggered: {alert.message}
            Severity: {alert.severity}
            Current value: {alert.current_value}
            Threshold: {alert.threshold}

            Recent system metrics:
            {json.dumps([m.dict() for m in recent_metrics[-5:]], indent=2, default=str)}

            Provide:
            1. Root cause analysis
            2. Immediate action recommendations
            3. Long-term optimization suggestions
            4. Related system components to check

            Respond in JSON format:
            {{
                "root_cause": "likely_cause_description",
                "immediate_actions": ["action1", "action2"],
                "optimization_suggestions": ["suggestion1", "suggestion2"],
                "related_components": ["component1", "component2"]
            }}
            """

            response = await self._generate_response(analysis_prompt)
            analysis_result = self._parse_ai_response(response)

            self.logger.info(f"Alert analysis for {alert.rule_name}: {analysis_result.content}")

        except Exception as e:
            self.logger.error(f"Error analyzing alert: {e}")

    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "metrics_collected": len(self.metrics_history),
            "active_alerts": len(self.active_alerts),
            "alert_rules": len(self.alert_rules),
            "last_metrics": self.metrics_history[-1].dict() if self.metrics_history else None
        }

    async def process_monitoring_request(self, request: str) -> AIResponse:
        """Process monitoring-related requests"""
        # Add monitoring context to the request
        context = {
            "monitoring_status": await self.get_monitoring_status(),
            "recent_metrics": [m.dict() for m in self.metrics_history[-5:]] if self.metrics_history else [],
            "active_alerts": [a.dict() for a in self.active_alerts[-5:]]
        }

        return await self.process_request(request, context)