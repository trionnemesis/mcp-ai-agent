"""
MCP Server with Linux System Operation Tools
Provides standardized tools for system administration
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import psutil
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Initialize server
server = Server("linux-system-tools")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available system tools"""
    return [
        Tool(
            name="get_system_info",
            description="Get comprehensive system information including CPU, memory, disk usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed information",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="monitor_processes",
            description="Monitor running processes with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_name": {
                        "type": "string",
                        "description": "Filter processes by name"
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort by: cpu, memory, pid, name",
                        "default": "cpu"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Limit number of results",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="manage_service",
            description="Manage systemd services (start, stop, restart, status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["start", "stop", "restart", "status", "enable", "disable"]
                    }
                },
                "required": ["service_name", "action"]
            }
        ),
        Tool(
            name="check_logs",
            description="Check system logs using journalctl",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Specific service to check logs for"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of lines to retrieve",
                        "default": 50
                    },
                    "follow": {
                        "type": "boolean",
                        "description": "Follow logs in real-time",
                        "default": False
                    },
                    "priority": {
                        "type": "string",
                        "description": "Log priority level",
                        "enum": ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]
                    }
                }
            }
        ),
        Tool(
            name="file_operations",
            description="Perform file and directory operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform",
                        "enum": ["list", "create", "delete", "copy", "move", "permissions"]
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target path for copy/move operations"
                    },
                    "permissions": {
                        "type": "string",
                        "description": "Permissions in octal format (e.g., 755)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Apply operation recursively",
                        "default": False
                    }
                },
                "required": ["operation", "path"]
            }
        ),
        Tool(
            name="network_diagnostics",
            description="Perform network diagnostics and monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Diagnostic operation",
                        "enum": ["ping", "traceroute", "netstat", "ss", "iptables_list", "interfaces"]
                    },
                    "target": {
                        "type": "string",
                        "description": "Target host for ping/traceroute"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of packets for ping",
                        "default": 4
                    }
                },
                "required": ["operation"]
            }
        ),
        Tool(
            name="disk_management",
            description="Disk space analysis and management",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Disk operation",
                        "enum": ["usage", "free", "mount", "unmount", "fsck"]
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to analyze or mount point"
                    },
                    "device": {
                        "type": "string",
                        "description": "Device to mount/unmount"
                    }
                },
                "required": ["operation"]
            }
        ),
        Tool(
            name="execute_command",
            description="Execute system commands with safety checks",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory for command execution"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
    """Handle tool execution"""
    try:
        if name == "get_system_info":
            return await get_system_info(arguments or {})
        elif name == "monitor_processes":
            return await monitor_processes(arguments or {})
        elif name == "manage_service":
            return await manage_service(arguments or {})
        elif name == "check_logs":
            return await check_logs(arguments or {})
        elif name == "file_operations":
            return await file_operations(arguments or {})
        elif name == "network_diagnostics":
            return await network_diagnostics(arguments or {})
        elif name == "disk_management":
            return await disk_management(arguments or {})
        elif name == "execute_command":
            return await execute_command(arguments or {})
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_system_info(args: Dict[str, Any]) -> List[TextContent]:
    """Get comprehensive system information"""
    detailed = args.get("detailed", False)

    try:
        # Basic system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        boot_time = psutil.boot_time()

        info = {
            "cpu_usage_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "boot_time": boot_time
        }

        if detailed:
            # Add detailed information
            info.update({
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else "N/A",
                "swap": psutil.swap_memory()._asdict(),
                "network_io": psutil.net_io_counters()._asdict(),
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else "N/A"
            })

        return [TextContent(type="text", text=json.dumps(info, indent=2, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting system info: {str(e)}")]


async def monitor_processes(args: Dict[str, Any]) -> List[TextContent]:
    """Monitor running processes"""
    try:
        filter_name = args.get("filter_name")
        sort_by = args.get("sort_by", "cpu")
        limit = args.get("limit", 10)

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                if filter_name and filter_name.lower() not in pinfo['name'].lower():
                    continue
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort processes
        sort_key_map = {
            "cpu": "cpu_percent",
            "memory": "memory_percent",
            "pid": "pid",
            "name": "name"
        }

        if sort_by in sort_key_map:
            processes.sort(key=lambda x: x[sort_key_map[sort_by]], reverse=True)

        # Limit results
        processes = processes[:limit]

        return [TextContent(type="text", text=json.dumps(processes, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error monitoring processes: {str(e)}")]


async def manage_service(args: Dict[str, Any]) -> List[TextContent]:
    """Manage systemd services"""
    try:
        service_name = args["service_name"]
        action = args["action"]

        # Validate service name
        if not service_name.replace("-", "").replace("_", "").replace(".", "").isalnum():
            return [TextContent(type="text", text="Invalid service name")]

        cmd = ["systemctl", action, service_name]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        return [TextContent(type="text", text=f"Service {action} result:\n{output}")]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Service operation timed out")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error managing service: {str(e)}")]


async def check_logs(args: Dict[str, Any]) -> List[TextContent]:
    """Check system logs using journalctl"""
    try:
        service = args.get("service")
        lines = args.get("lines", 50)
        priority = args.get("priority")

        cmd = ["journalctl", "-n", str(lines)]

        if service:
            cmd.extend(["-u", service])

        if priority:
            cmd.extend(["-p", priority])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        return [TextContent(type="text", text=result.stdout)]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Log retrieval timed out")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error checking logs: {str(e)}")]


async def file_operations(args: Dict[str, Any]) -> List[TextContent]:
    """Perform file and directory operations"""
    try:
        operation = args["operation"]
        path = args["path"]

        if operation == "list":
            if os.path.exists(path):
                items = os.listdir(path)
                return [TextContent(type="text", text=json.dumps(items, indent=2))]
            else:
                return [TextContent(type="text", text=f"Path does not exist: {path}")]

        elif operation == "create":
            if os.path.exists(path):
                return [TextContent(type="text", text=f"Path already exists: {path}")]

            if path.endswith('/'):
                os.makedirs(path, exist_ok=True)
                return [TextContent(type="text", text=f"Directory created: {path}")]
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write("")
                return [TextContent(type="text", text=f"File created: {path}")]

        else:
            return [TextContent(type="text", text=f"Operation {operation} not yet implemented")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error in file operation: {str(e)}")]


async def network_diagnostics(args: Dict[str, Any]) -> List[TextContent]:
    """Perform network diagnostics"""
    try:
        operation = args["operation"]

        if operation == "ping":
            target = args.get("target", "8.8.8.8")
            count = args.get("count", 4)

            cmd = ["ping", "-c", str(count), target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return [TextContent(type="text", text=result.stdout)]

        elif operation == "interfaces":
            interfaces = psutil.net_if_addrs()
            return [TextContent(type="text", text=json.dumps(interfaces, indent=2, default=str))]

        elif operation == "netstat":
            cmd = ["netstat", "-tuln"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return [TextContent(type="text", text=result.stdout)]

        else:
            return [TextContent(type="text", text=f"Network operation {operation} not yet implemented")]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Network operation timed out")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error in network diagnostics: {str(e)}")]


async def disk_management(args: Dict[str, Any]) -> List[TextContent]:
    """Disk space analysis and management"""
    try:
        operation = args["operation"]

        if operation == "usage":
            path = args.get("path", "/")

            if os.path.exists(path):
                usage = psutil.disk_usage(path)
                result = {
                    "path": path,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text=f"Path does not exist: {path}")]

        elif operation == "free":
            partitions = psutil.disk_partitions()
            result = []

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100
                    })
                except PermissionError:
                    continue

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type="text", text=f"Disk operation {operation} not yet implemented")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error in disk management: {str(e)}")]


async def execute_command(args: Dict[str, Any]) -> List[TextContent]:
    """Execute system commands with safety checks"""
    try:
        command = args["command"]
        working_dir = args.get("working_dir", os.getcwd())
        timeout = args.get("timeout", 30)

        # Basic safety checks
        dangerous_commands = ["rm -rf /", "dd if=", "mkfs", "fdisk", ":(){ :|:& };:"]
        if any(dangerous in command for dangerous in dangerous_commands):
            return [TextContent(type="text", text="Command blocked for safety reasons")]

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )

        output = f"Exit code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Command execution timed out")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing command: {str(e)}")]


async def main():
    """Main server entry point"""
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="linux-system-tools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())