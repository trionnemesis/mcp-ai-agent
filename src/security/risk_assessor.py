"""
Security Risk Assessment Module
Provides multi-layer security checks and risk evaluation
"""

import re
import logging
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from pydantic import BaseModel

from ..utils.config import Config


class RiskLevel(Enum):
    """Risk levels for operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityRule(BaseModel):
    """Security rule definition"""
    name: str
    pattern: str
    risk_level: RiskLevel
    description: str
    whitelist: List[str] = []


class RiskAssessment(BaseModel):
    """Risk assessment result"""
    risk_level: RiskLevel
    reasons: List[str]
    blocked: bool = False
    requires_confirmation: bool = False


class RiskAssessor:
    """
    Multi-layer security risk assessor
    Evaluates commands and operations for potential security risks
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.security_rules = self._load_security_rules()
        self.dangerous_commands = self._load_dangerous_commands()

    def _load_security_rules(self) -> List[SecurityRule]:
        """Load security rules for risk assessment"""
        return [
            SecurityRule(
                name="destructive_file_operations",
                pattern=r"rm\s+(-[rf]+|--recursive|--force).*",
                risk_level=RiskLevel.HIGH,
                description="Destructive file deletion operations"
            ),
            SecurityRule(
                name="system_modification",
                pattern=r"(sudo|su)\s+.*",
                risk_level=RiskLevel.HIGH,
                description="Operations requiring elevated privileges"
            ),
            SecurityRule(
                name="network_operations",
                pattern=r"(wget|curl|nc|netcat|ssh|scp|rsync).*",
                risk_level=RiskLevel.MEDIUM,
                description="Network operations that may transfer data"
            ),
            SecurityRule(
                name="process_manipulation",
                pattern=r"(kill|killall|pkill)\s+(-9|--kill).*",
                risk_level=RiskLevel.MEDIUM,
                description="Forceful process termination"
            ),
            SecurityRule(
                name="disk_operations",
                pattern=r"(mkfs|fdisk|dd|parted|gparted).*",
                risk_level=RiskLevel.CRITICAL,
                description="Disk partitioning and formatting operations"
            ),
            SecurityRule(
                name="service_management",
                pattern=r"systemctl\s+(start|stop|restart|disable).*",
                risk_level=RiskLevel.MEDIUM,
                description="System service management"
            ),
            SecurityRule(
                name="package_management",
                pattern=r"(apt|yum|dnf|pacman|pip)\s+(install|remove|purge).*",
                risk_level=RiskLevel.MEDIUM,
                description="Package installation or removal"
            ),
            SecurityRule(
                name="cron_manipulation",
                pattern=r"crontab\s+(-[er]|--edit|--remove).*",
                risk_level=RiskLevel.MEDIUM,
                description="Cron job modification"
            ),
            SecurityRule(
                name="user_management",
                pattern=r"(useradd|userdel|usermod|passwd|chpasswd).*",
                risk_level=RiskLevel.HIGH,
                description="User account management"
            ),
            SecurityRule(
                name="firewall_changes",
                pattern=r"(iptables|ufw|firewall-cmd).*",
                risk_level=RiskLevel.HIGH,
                description="Firewall configuration changes"
            )
        ]

    def _load_dangerous_commands(self) -> Set[str]:
        """Load list of dangerous command patterns"""
        return {
            "rm -rf /",
            "dd if=/dev/zero",
            "dd if=/dev/random",
            ":(){ :|:& };:",  # Fork bomb
            "mkfs",
            "format",
            "fdisk",
            "shutdown -h now",
            "reboot",
            "halt",
            "init 0",
            "init 6"
        }

    async def assess_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Assess risk level of a tool call

        Args:
            tool_name: Name of the tool to be executed
            arguments: Tool arguments

        Returns:
            Risk level as string (low, medium, high, critical)
        """
        try:
            assessment = RiskAssessment(
                risk_level=RiskLevel.LOW,
                reasons=[]
            )

            # Check tool-specific risks
            assessment = await self._assess_tool_specific_risks(tool_name, arguments, assessment)

            # Check command content if executing commands
            if tool_name == "execute_command" and "command" in arguments:
                command = arguments["command"]
                assessment = await self._assess_command_risks(command, assessment)

            # Check file operations
            if tool_name == "file_operations":
                assessment = await self._assess_file_operation_risks(arguments, assessment)

            # Check service management
            if tool_name == "manage_service":
                assessment = await self._assess_service_risks(arguments, assessment)

            self.logger.info(f"Risk assessment for {tool_name}: {assessment.risk_level.value}")
            return assessment.risk_level.value

        except Exception as e:
            self.logger.error(f"Error in risk assessment: {e}")
            return RiskLevel.HIGH.value

    async def _assess_tool_specific_risks(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        assessment: RiskAssessment
    ) -> RiskAssessment:
        """Assess risks specific to tool type"""

        tool_risk_levels = {
            "get_system_info": RiskLevel.LOW,
            "monitor_processes": RiskLevel.LOW,
            "check_logs": RiskLevel.LOW,
            "network_diagnostics": RiskLevel.MEDIUM,
            "disk_management": RiskLevel.MEDIUM,
            "file_operations": RiskLevel.MEDIUM,
            "manage_service": RiskLevel.HIGH,
            "execute_command": RiskLevel.HIGH
        }

        base_risk = tool_risk_levels.get(tool_name, RiskLevel.MEDIUM)

        if base_risk.value == "high" or base_risk.value == "critical":
            assessment.risk_level = base_risk
            assessment.reasons.append(f"Tool {tool_name} has inherent high risk level")

        return assessment

    async def _assess_command_risks(self, command: str, assessment: RiskAssessment) -> RiskAssessment:
        """Assess risks in command execution"""

        # Check against dangerous command patterns
        for dangerous_cmd in self.dangerous_commands:
            if dangerous_cmd in command:
                assessment.risk_level = RiskLevel.CRITICAL
                assessment.reasons.append(f"Contains dangerous pattern: {dangerous_cmd}")
                assessment.blocked = True
                return assessment

        # Check against security rules
        for rule in self.security_rules:
            if re.search(rule.pattern, command, re.IGNORECASE):
                if rule.risk_level.value == "critical":
                    assessment.risk_level = RiskLevel.CRITICAL
                    assessment.blocked = True
                elif rule.risk_level.value == "high" and assessment.risk_level != RiskLevel.CRITICAL:
                    assessment.risk_level = RiskLevel.HIGH
                elif rule.risk_level.value == "medium" and assessment.risk_level == RiskLevel.LOW:
                    assessment.risk_level = RiskLevel.MEDIUM

                assessment.reasons.append(f"Matches rule: {rule.description}")

        # Check for command injection patterns
        injection_patterns = [
            r";.*",      # Command chaining
            r"\|.*",     # Piping
            r"&&.*",     # Conditional execution
            r"\$\(",     # Command substitution
            r"`.*`",     # Backtick execution
        ]

        for pattern in injection_patterns:
            if re.search(pattern, command):
                if assessment.risk_level == RiskLevel.LOW:
                    assessment.risk_level = RiskLevel.MEDIUM
                assessment.reasons.append("Contains potential command injection pattern")

        return assessment

    async def _assess_file_operation_risks(
        self,
        arguments: Dict[str, Any],
        assessment: RiskAssessment
    ) -> RiskAssessment:
        """Assess risks in file operations"""

        operation = arguments.get("operation", "")
        path = arguments.get("path", "")

        # Critical system paths
        critical_paths = [
            "/etc",
            "/boot",
            "/sys",
            "/proc",
            "/dev",
            "/usr/bin",
            "/usr/sbin",
            "/bin",
            "/sbin"
        ]

        for critical_path in critical_paths:
            if path.startswith(critical_path):
                assessment.risk_level = RiskLevel.HIGH
                assessment.reasons.append(f"Operation on critical system path: {critical_path}")

        # Destructive operations
        if operation in ["delete", "move"] and path == "/":
            assessment.risk_level = RiskLevel.CRITICAL
            assessment.blocked = True
            assessment.reasons.append("Attempted operation on root directory")

        return assessment

    async def _assess_service_risks(
        self,
        arguments: Dict[str, Any],
        assessment: RiskAssessment
    ) -> RiskAssessment:
        """Assess risks in service management"""

        service_name = arguments.get("service_name", "")
        action = arguments.get("action", "")

        # Critical services
        critical_services = [
            "ssh",
            "sshd",
            "networking",
            "network-manager",
            "systemd-networkd",
            "firewall",
            "iptables"
        ]

        if service_name in critical_services:
            if action in ["stop", "disable"]:
                assessment.risk_level = RiskLevel.HIGH
                assessment.reasons.append(f"Stopping/disabling critical service: {service_name}")

        return assessment

    def is_whitelisted(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Check if operation is whitelisted"""
        whitelist = getattr(self.config, 'dangerous_commands_whitelist', [])

        if tool_name == "execute_command":
            command = arguments.get("command", "")
            return command in whitelist

        return False

    async def should_block_operation(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Determine if operation should be blocked"""
        assessment_result = await self.assess_tool_call(tool_name, arguments)

        if assessment_result == "critical":
            return True

        if not self.config.enable_risk_assessment:
            return False

        if self.is_whitelisted(tool_name, arguments):
            return False

        return assessment_result in ["high", "critical"]

    async def requires_confirmation(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Determine if operation requires user confirmation"""
        if not self.config.require_confirmation:
            return False

        assessment_result = await self.assess_tool_call(tool_name, arguments)
        return assessment_result in ["medium", "high"]