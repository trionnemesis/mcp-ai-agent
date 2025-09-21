"""
Extended MCP Tools for Advanced Linux Operations
Comprehensive system administration tools
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import time
from typing import Any, Dict, List, Optional

import psutil
from mcp.types import TextContent


logger = logging.getLogger(__name__)


class ExtendedSystemTools:
    """Extended system tools for comprehensive Linux administration"""

    @staticmethod
    async def advanced_process_management(args: Dict[str, Any]) -> List[TextContent]:
        """Advanced process management and analysis"""
        try:
            operation = args.get("operation", "list")

            if operation == "list":
                return await ExtendedSystemTools._list_processes_detailed(args)
            elif operation == "analyze":
                return await ExtendedSystemTools._analyze_process_tree(args)
            elif operation == "kill":
                return await ExtendedSystemTools._terminate_process_safe(args)
            elif operation == "resource_hogs":
                return await ExtendedSystemTools._find_resource_hogs(args)
            else:
                return [TextContent(type="text", text=f"Unknown operation: {operation}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error in process management: {str(e)}")]

    @staticmethod
    async def _list_processes_detailed(args: Dict[str, Any]) -> List[TextContent]:
        """List processes with detailed information"""
        filter_user = args.get("user")
        min_cpu = args.get("min_cpu", 0)
        min_memory = args.get("min_memory", 0)

        processes = []
        for proc in psutil.process_iter([
            'pid', 'name', 'username', 'cpu_percent', 'memory_percent',
            'memory_info', 'create_time', 'status', 'num_threads', 'cmdline'
        ]):
            try:
                pinfo = proc.info

                # Apply filters
                if filter_user and pinfo['username'] != filter_user:
                    continue
                if pinfo['cpu_percent'] < min_cpu:
                    continue
                if pinfo['memory_percent'] < min_memory:
                    continue

                # Add additional info
                pinfo['create_time_formatted'] = time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.localtime(pinfo['create_time'])
                )
                pinfo['memory_mb'] = pinfo['memory_info'].rss / 1024 / 1024

                processes.append(pinfo)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        return [TextContent(type="text", text=json.dumps(processes, indent=2, default=str))]

    @staticmethod
    async def _find_resource_hogs(args: Dict[str, Any]) -> List[TextContent]:
        """Find processes consuming excessive resources"""
        cpu_threshold = args.get("cpu_threshold", 50)
        memory_threshold = args.get("memory_threshold", 20)

        resource_hogs = {
            "cpu_hogs": [],
            "memory_hogs": [],
            "combined_hogs": []
        }

        for proc in psutil.process_iter([
            'pid', 'name', 'cpu_percent', 'memory_percent', 'username'
        ]):
            try:
                pinfo = proc.info

                if pinfo['cpu_percent'] > cpu_threshold:
                    resource_hogs["cpu_hogs"].append(pinfo)

                if pinfo['memory_percent'] > memory_threshold:
                    resource_hogs["memory_hogs"].append(pinfo)

                if (pinfo['cpu_percent'] > cpu_threshold/2 and
                    pinfo['memory_percent'] > memory_threshold/2):
                    resource_hogs["combined_hogs"].append(pinfo)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return [TextContent(type="text", text=json.dumps(resource_hogs, indent=2))]

    @staticmethod
    async def system_performance_analysis(args: Dict[str, Any]) -> List[TextContent]:
        """Comprehensive system performance analysis"""
        try:
            analysis_type = args.get("type", "full")
            duration = args.get("duration", 10)

            if analysis_type == "full":
                return await ExtendedSystemTools._full_performance_analysis(duration)
            elif analysis_type == "io":
                return await ExtendedSystemTools._io_performance_analysis(duration)
            elif analysis_type == "network":
                return await ExtendedSystemTools._network_performance_analysis(duration)
            else:
                return [TextContent(type="text", text=f"Unknown analysis type: {analysis_type}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error in performance analysis: {str(e)}")]

    @staticmethod
    async def _full_performance_analysis(duration: int) -> List[TextContent]:
        """Full system performance analysis"""
        analysis_results = {
            "analysis_duration": duration,
            "timestamp": time.time(),
            "cpu_analysis": {},
            "memory_analysis": {},
            "disk_analysis": {},
            "network_analysis": {}
        }

        # CPU Analysis
        cpu_before = psutil.cpu_times()
        cpu_percent_samples = []

        # Memory Analysis
        memory = psutil.virtual_memory()
        analysis_results["memory_analysis"] = {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_percent": memory.percent,
            "swap": psutil.swap_memory()._asdict()
        }

        # Disk Analysis
        disk_io_before = psutil.disk_io_counters()

        # Network Analysis
        net_io_before = psutil.net_io_counters()

        # Sample data over duration
        for i in range(duration):
            cpu_percent_samples.append(psutil.cpu_percent(interval=1))

        # Final measurements
        cpu_after = psutil.cpu_times()
        disk_io_after = psutil.disk_io_counters()
        net_io_after = psutil.net_io_counters()

        # CPU analysis results
        analysis_results["cpu_analysis"] = {
            "average_usage": sum(cpu_percent_samples) / len(cpu_percent_samples),
            "max_usage": max(cpu_percent_samples),
            "min_usage": min(cpu_percent_samples),
            "samples": cpu_percent_samples,
            "cores": psutil.cpu_count(),
            "logical_cores": psutil.cpu_count(logical=True)
        }

        # Disk I/O analysis
        if disk_io_before and disk_io_after:
            analysis_results["disk_analysis"] = {
                "read_bytes_per_sec": (disk_io_after.read_bytes - disk_io_before.read_bytes) / duration,
                "write_bytes_per_sec": (disk_io_after.write_bytes - disk_io_before.write_bytes) / duration,
                "read_ops_per_sec": (disk_io_after.read_count - disk_io_before.read_count) / duration,
                "write_ops_per_sec": (disk_io_after.write_count - disk_io_before.write_count) / duration
            }

        # Network I/O analysis
        if net_io_before and net_io_after:
            analysis_results["network_analysis"] = {
                "bytes_sent_per_sec": (net_io_after.bytes_sent - net_io_before.bytes_sent) / duration,
                "bytes_recv_per_sec": (net_io_after.bytes_recv - net_io_before.bytes_recv) / duration,
                "packets_sent_per_sec": (net_io_after.packets_sent - net_io_before.packets_sent) / duration,
                "packets_recv_per_sec": (net_io_after.packets_recv - net_io_before.packets_recv) / duration
            }

        return [TextContent(type="text", text=json.dumps(analysis_results, indent=2, default=str))]

    @staticmethod
    async def security_audit_tools(args: Dict[str, Any]) -> List[TextContent]:
        """Security audit and compliance checking tools"""
        try:
            audit_type = args.get("type", "basic")

            if audit_type == "basic":
                return await ExtendedSystemTools._basic_security_audit()
            elif audit_type == "permissions":
                return await ExtendedSystemTools._file_permissions_audit(args)
            elif audit_type == "network":
                return await ExtendedSystemTools._network_security_audit()
            elif audit_type == "users":
                return await ExtendedSystemTools._user_security_audit()
            else:
                return [TextContent(type="text", text=f"Unknown audit type: {audit_type}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error in security audit: {str(e)}")]

    @staticmethod
    async def _basic_security_audit() -> List[TextContent]:
        """Basic security audit checks"""
        audit_results = {
            "timestamp": time.time(),
            "checks": []
        }

        # Check for world-writable files
        try:
            result = subprocess.run(
                ["find", "/", "-type", "f", "-perm", "-002", "2>/dev/null"],
                capture_output=True, text=True, timeout=30
            )
            world_writable = result.stdout.strip().split('\n') if result.stdout.strip() else []
            audit_results["checks"].append({
                "name": "world_writable_files",
                "status": "pass" if not world_writable else "fail",
                "count": len(world_writable),
                "files": world_writable[:10]  # First 10 files
            })
        except subprocess.TimeoutExpired:
            audit_results["checks"].append({
                "name": "world_writable_files",
                "status": "timeout",
                "error": "Search timed out"
            })

        # Check SSH configuration
        ssh_config_path = "/etc/ssh/sshd_config"
        if os.path.exists(ssh_config_path):
            try:
                with open(ssh_config_path, 'r') as f:
                    ssh_config = f.read()

                ssh_checks = {
                    "root_login_disabled": "PermitRootLogin no" in ssh_config,
                    "password_auth_disabled": "PasswordAuthentication no" in ssh_config,
                    "protocol_2_only": "Protocol 2" in ssh_config or "Protocol 1" not in ssh_config
                }

                audit_results["checks"].append({
                    "name": "ssh_security",
                    "status": "checked",
                    "details": ssh_checks
                })
            except Exception as e:
                audit_results["checks"].append({
                    "name": "ssh_security",
                    "status": "error",
                    "error": str(e)
                })

        # Check for sudo access
        try:
            result = subprocess.run(
                ["getent", "group", "sudo"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                sudo_users = result.stdout.strip().split(':')[-1].split(',') if result.stdout.strip() else []
                audit_results["checks"].append({
                    "name": "sudo_users",
                    "status": "checked",
                    "users": [u.strip() for u in sudo_users if u.strip()]
                })
        except Exception as e:
            audit_results["checks"].append({
                "name": "sudo_users",
                "status": "error",
                "error": str(e)
            })

        return [TextContent(type="text", text=json.dumps(audit_results, indent=2))]

    @staticmethod
    async def log_analysis_tools(args: Dict[str, Any]) -> List[TextContent]:
        """Advanced log analysis and monitoring tools"""
        try:
            analysis_type = args.get("type", "errors")
            log_file = args.get("log_file")
            pattern = args.get("pattern")
            time_range = args.get("time_range", "1h")

            if analysis_type == "errors":
                return await ExtendedSystemTools._analyze_error_logs(log_file, time_range)
            elif analysis_type == "pattern":
                return await ExtendedSystemTools._search_log_patterns(log_file, pattern)
            elif analysis_type == "summary":
                return await ExtendedSystemTools._log_summary_analysis(log_file, time_range)
            else:
                return [TextContent(type="text", text=f"Unknown analysis type: {analysis_type}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error in log analysis: {str(e)}")]

    @staticmethod
    async def _analyze_error_logs(log_file: Optional[str], time_range: str) -> List[TextContent]:
        """Analyze system logs for errors and warnings"""
        analysis_results = {
            "time_range": time_range,
            "error_patterns": [],
            "warning_patterns": [],
            "critical_events": []
        }

        # Use journalctl if no specific log file provided
        if not log_file:
            cmd = ["journalctl", f"--since={time_range}", "-p", "err"]
        else:
            # Analyze specific log file
            cmd = ["tail", "-n", "1000", log_file]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            log_lines = result.stdout.split('\n')

            # Error patterns to look for
            error_patterns = [
                r'(?i)error',
                r'(?i)fail',
                r'(?i)exception',
                r'(?i)critical',
                r'(?i)fatal',
                r'(?i)panic'
            ]

            for line in log_lines:
                for pattern in error_patterns:
                    if re.search(pattern, line):
                        analysis_results["error_patterns"].append({
                            "line": line.strip(),
                            "pattern": pattern
                        })
                        break

            # Count patterns
            pattern_counts = {}
            for entry in analysis_results["error_patterns"]:
                pattern = entry["pattern"]
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

            analysis_results["pattern_summary"] = pattern_counts
            analysis_results["total_errors"] = len(analysis_results["error_patterns"])

        except subprocess.TimeoutExpired:
            analysis_results["error"] = "Log analysis timed out"
        except Exception as e:
            analysis_results["error"] = str(e)

        return [TextContent(type="text", text=json.dumps(analysis_results, indent=2))]

    @staticmethod
    async def backup_and_recovery_tools(args: Dict[str, Any]) -> List[TextContent]:
        """Backup and recovery management tools"""
        try:
            operation = args.get("operation", "create")
            source_path = args.get("source_path")
            backup_path = args.get("backup_path")
            compression = args.get("compression", "gzip")

            if operation == "create":
                return await ExtendedSystemTools._create_backup(source_path, backup_path, compression)
            elif operation == "restore":
                return await ExtendedSystemTools._restore_backup(backup_path, source_path)
            elif operation == "verify":
                return await ExtendedSystemTools._verify_backup(backup_path)
            elif operation == "list":
                return await ExtendedSystemTools._list_backups(backup_path)
            else:
                return [TextContent(type="text", text=f"Unknown operation: {operation}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error in backup operation: {str(e)}")]

    @staticmethod
    async def _create_backup(source_path: str, backup_path: str, compression: str) -> List[TextContent]:
        """Create system backup"""
        if not source_path or not backup_path:
            return [TextContent(type="text", text="Source and backup paths are required")]

        backup_info = {
            "source_path": source_path,
            "backup_path": backup_path,
            "timestamp": time.strftime('%Y%m%d_%H%M%S'),
            "compression": compression
        }

        # Create backup filename with timestamp
        backup_filename = f"backup_{backup_info['timestamp']}.tar"
        if compression == "gzip":
            backup_filename += ".gz"
            tar_option = "czf"
        elif compression == "bzip2":
            backup_filename += ".bz2"
            tar_option = "cjf"
        else:
            tar_option = "cf"

        full_backup_path = os.path.join(backup_path, backup_filename)

        try:
            # Ensure backup directory exists
            os.makedirs(backup_path, exist_ok=True)

            # Create backup
            cmd = ["tar", tar_option, full_backup_path, "-C", os.path.dirname(source_path), os.path.basename(source_path)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Get backup file info
                stat_info = os.stat(full_backup_path)
                backup_info.update({
                    "status": "success",
                    "backup_file": full_backup_path,
                    "size_bytes": stat_info.st_size,
                    "size_mb": stat_info.st_size / (1024 * 1024)
                })
            else:
                backup_info.update({
                    "status": "failed",
                    "error": result.stderr
                })

        except subprocess.TimeoutExpired:
            backup_info.update({
                "status": "failed",
                "error": "Backup operation timed out"
            })
        except Exception as e:
            backup_info.update({
                "status": "failed",
                "error": str(e)
            })

        return [TextContent(type="text", text=json.dumps(backup_info, indent=2))]

    @staticmethod
    async def container_management_tools(args: Dict[str, Any]) -> List[TextContent]:
        """Docker and container management tools"""
        try:
            operation = args.get("operation", "list")

            if operation == "list":
                return await ExtendedSystemTools._list_containers()
            elif operation == "stats":
                return await ExtendedSystemTools._container_stats()
            elif operation == "logs":
                return await ExtendedSystemTools._container_logs(args)
            elif operation == "cleanup":
                return await ExtendedSystemTools._cleanup_containers()
            else:
                return [TextContent(type="text", text=f"Unknown operation: {operation}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error in container management: {str(e)}")]

    @staticmethod
    async def _list_containers() -> List[TextContent]:
        """List Docker containers"""
        try:
            # Check if Docker is available
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return [TextContent(type="text", text="Docker is not available on this system")]

            # List containers
            cmd = ["docker", "ps", "-a", "--format", "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Names}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return [TextContent(type="text", text=result.stdout)]
            else:
                return [TextContent(type="text", text=f"Error listing containers: {result.stderr}")]

        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text="Container listing timed out")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]