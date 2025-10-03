"""
一個具備 Linux 系統操作工具的 MCP (機器控制通訊協定) 伺服器。
此伺服器提供了一套標準化的工具，用於進行系統管理任務。
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


# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# 初始化伺服器
server = Server("linux-system-tools")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出所有可用的系統工具。"""
    return [
        Tool(
            name="get_system_info",
            description="獲取全面的系統資訊，包括 CPU、記憶體、磁碟使用情況等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "是否回傳詳細資訊。若為 true，將包含更深入的系統數據。",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="monitor_processes",
            description="監控正在運行的行程，並提供過濾與排序選項。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_name": {
                        "type": "string",
                        "description": "根據行程名稱進行過濾。只會顯示名稱包含此字串的行程。"
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "排序依據：可選 'cpu' (CPU使用率), 'memory' (記憶體使用率), 'pid' (行程ID), 'name' (名稱)。",
                        "default": "cpu"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "限制回傳結果的數量。",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="manage_service",
            description="管理 systemd 服務，例如啟動、停止、重啟或查看狀態。",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "要操作的服務名稱。"
                    },
                    "action": {
                        "type": "string",
                        "description": "要執行的操作。",
                        "enum": ["start", "stop", "restart", "status", "enable", "disable"]
                    }
                },
                "required": ["service_name", "action"]
            }
        ),
        Tool(
            name="check_logs",
            description="使用 journalctl 檢查系統日誌。",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "指定要檢查日誌的服務名稱。"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "要檢索的日誌行數。",
                        "default": 50
                    },
                    "follow": {
                        "type": "boolean",
                        "description": "是否即時追蹤新的日誌輸出。",
                        "default": False
                    },
                    "priority": {
                        "type": "string",
                        "description": "日誌的優先級別。",
                        "enum": ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]
                    }
                }
            }
        ),
        Tool(
            name="file_operations",
            description="執行檔案與目錄的相關操作。",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "要執行的操作。",
                        "enum": ["list", "create", "delete", "copy", "move", "permissions"]
                    },
                    "path": {
                        "type": "string",
                        "description": "檔案或目錄的路徑。"
                    },
                    "target": {
                        "type": "string",
                        "description": "複製或移動操作的目標路徑。"
                    },
                    "permissions": {
                        "type": "string",
                        "description": "以八進位格式表示的權限（例如 '755'）。"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "是否遞迴地執行操作。",
                        "default": False
                    }
                },
                "required": ["operation", "path"]
            }
        ),
        Tool(
            name="network_diagnostics",
            description="執行網路診斷與監控。",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "要執行的診斷操作。",
                        "enum": ["ping", "traceroute", "netstat", "ss", "iptables_list", "interfaces"]
                    },
                    "target": {
                        "type": "string",
                        "description": "ping 或 traceroute 的目標主機。"
                    },
                    "count": {
                        "type": "integer",
                        "description": "ping 操作要發送的封包數量。",
                        "default": 4
                    }
                },
                "required": ["operation"]
            }
        ),
        Tool(
            name="disk_management",
            description="進行磁碟空間分析與管理。",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "要執行的磁碟操作。",
                        "enum": ["usage", "free", "mount", "unmount", "fsck"]
                    },
                    "path": {
                        "type": "string",
                        "description": "要分析的路徑或掛載點。"
                    },
                    "device": {
                        "type": "string",
                        "description": "要掛載或卸載的裝置。"
                    }
                },
                "required": ["operation"]
            }
        ),
        Tool(
            name="execute_command",
            description="執行系統指令，並包含安全檢查。",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要執行的指令字串。"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "執行指令時的工作目錄。"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "指令執行的超時時間（秒）。",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
    """處理工具執行請求。"""
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
            raise ValueError(f"未知的工具: {name}")

    except Exception as e:
        logger.error(f"執行工具 {name} 時發生錯誤: {e}")
        return [TextContent(type="text", text=f"錯誤: {str(e)}")]


async def get_system_info(args: Dict[str, Any]) -> List[TextContent]:
    """獲取全面的系統資訊。"""
    detailed = args.get("detailed", False)

    try:
        # 獲取基本系統資訊
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
            # 新增詳細資訊
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
        return [TextContent(type="text", text=f"獲取系統資訊時發生錯誤: {str(e)}")]


async def monitor_processes(args: Dict[str, Any]) -> List[TextContent]:
    """監控正在運行的行程。"""
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

        # 排序行程
        sort_key_map = {
            "cpu": "cpu_percent",
            "memory": "memory_percent",
            "pid": "pid",
            "name": "name"
        }

        if sort_by in sort_key_map:
            processes.sort(key=lambda x: x[sort_key_map[sort_by]], reverse=True)

        # 限制結果數量
        processes = processes[:limit]

        return [TextContent(type="text", text=json.dumps(processes, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"監控行程時發生錯誤: {str(e)}")]


async def manage_service(args: Dict[str, Any]) -> List[TextContent]:
    """管理 systemd 服務。"""
    try:
        service_name = args["service_name"]
        action = args["action"]

        # 驗證服務名稱的合法性
        if not service_name.replace("-", "").replace("_", "").replace(".", "").isalnum():
            return [TextContent(type="text", text="無效的服務名稱")]

        cmd = ["systemctl", action, service_name]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        return [TextContent(type="text", text=f"服務 {action} 操作結果:\n{output}")]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="服務操作超時")]
    except Exception as e:
        return [TextContent(type="text", text=f"管理服務時發生錯誤: {str(e)}")]


async def check_logs(args: Dict[str, Any]) -> List[TextContent]:
    """使用 journalctl 檢查系統日誌。"""
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
        return [TextContent(type="text", text="獲取日誌操作超時")]
    except Exception as e:
        return [TextContent(type="text", text=f"檢查日誌時發生錯誤: {str(e)}")]


async def file_operations(args: Dict[str, Any]) -> List[TextContent]:
    """執行檔案與目錄的操作。"""
    try:
        operation = args["operation"]
        path = args["path"]

        if operation == "list":
            if os.path.exists(path):
                items = os.listdir(path)
                return [TextContent(type="text", text=json.dumps(items, indent=2))]
            else:
                return [TextContent(type="text", text=f"路徑不存在: {path}")]

        elif operation == "create":
            if os.path.exists(path):
                return [TextContent(type="text", text=f"路徑已存在: {path}")]

            if path.endswith('/'):
                os.makedirs(path, exist_ok=True)
                return [TextContent(type="text", text=f"目錄已建立: {path}")]
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write("")
                return [TextContent(type="text", text=f"檔案已建立: {path}")]

        else:
            return [TextContent(type="text", text=f"操作 {operation} 尚未實現")]

    except Exception as e:
        return [TextContent(type="text", text=f"檔案操作時發生錯誤: {str(e)}")]


async def network_diagnostics(args: Dict[str, Any]) -> List[TextContent]:
    """執行網路診斷。"""
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
            return [TextContent(type="text", text=f"網路操作 {operation} 尚未實現")]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="網路操作超時")]
    except Exception as e:
        return [TextContent(type="text", text=f"網路診斷時發生錯誤: {str(e)}")]


async def disk_management(args: Dict[str, Any]) -> List[TextContent]:
    """進行磁碟空間分析與管理。"""
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
                return [TextContent(type="text", text=f"路徑不存在: {path}")]

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
            return [TextContent(type="text", text=f"磁碟操作 {operation} 尚未實現")]

    except Exception as e:
        return [TextContent(type="text", text=f"磁碟管理時發生錯誤: {str(e)}")]


async def execute_command(args: Dict[str, Any]) -> List[TextContent]:
    """執行系統指令，並包含安全檢查。"""
    try:
        command = args["command"]
        working_dir = args.get("working_dir", os.getcwd())
        timeout = args.get("timeout", 30)

        # 基本安全檢查，防止執行危險指令
        dangerous_commands = ["rm -rf /", "dd if=", "mkfs", "fdisk", ":(){ :|:& };:"]
        if any(dangerous in command for dangerous in dangerous_commands):
            return [TextContent(type="text", text="因安全考量，該指令已被封鎖")]

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )

        output = f"結束代碼: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="指令執行超時")]
    except Exception as e:
        return [TextContent(type="text", text=f"執行指令時發生錯誤: {str(e)}")]


async def main():
    """伺服器主程式進入點。"""
    # 透過 stdin/stdout 串流來執行伺服器
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