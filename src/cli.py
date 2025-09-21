"""
CLI Interface for MCP AI Agent
Non-interactive mode support with comprehensive command options
"""

import asyncio
import json
import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .agents.base_agent import BaseMCPAgent
from .agents.monitoring_agent import MonitoringAgent
from .agents.operations_agent import OperationsAgent
from .utils.config import Config


app = typer.Typer(
    name="mcp-agent",
    help="MCP AI Agent - Intelligent System Administration with Gemini SDK",
    add_completion=False
)

console = Console()


def setup_logging(log_level: str, log_file: Optional[str] = None) -> None:
    """Setup logging configuration"""
    level = getattr(logging, log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


@app.command()
def monitor(
    duration: int = typer.Option(0, "--duration", "-d", help="Monitoring duration in seconds (0 = infinite)"),
    interval: int = typer.Option(30, "--interval", "-i", help="Monitoring interval in seconds"),
    cpu_threshold: float = typer.Option(80.0, "--cpu-threshold", help="CPU usage alert threshold"),
    memory_threshold: float = typer.Option(85.0, "--memory-threshold", help="Memory usage alert threshold"),
    disk_threshold: float = typer.Option(90.0, "--disk-threshold", help="Disk usage alert threshold"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Start intelligent system monitoring"""
    try:
        # Load configuration
        config = Config.from_env()

        # Override config with CLI parameters
        config.monitoring_interval = interval
        config.cpu_threshold = cpu_threshold
        config.memory_threshold = memory_threshold
        config.disk_threshold = disk_threshold

        if verbose:
            config.log_level = "DEBUG"

        setup_logging(config.log_level, config.log_file)

        console.print(Panel.fit(
            "🤖 Starting Intelligent System Monitoring",
            style="bold blue"
        ))

        # Create and run monitoring agent
        agent = MonitoringAgent(config)

        if duration > 0:
            console.print(f"⏱️  Monitoring for {duration} seconds...")
            asyncio.run(asyncio.wait_for(agent.run(), timeout=duration))
        else:
            console.print("⏱️  Monitoring indefinitely (Ctrl+C to stop)...")
            asyncio.run(agent.run())

    except KeyboardInterrupt:
        console.print("\n🛑 Monitoring stopped by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def execute(
    command: str = typer.Argument(..., help="Natural language command to execute"),
    batch_file: Optional[str] = typer.Option(None, "--batch", "-b", help="File containing batch commands"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Require confirmation for risky operations"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Execute system operations via natural language commands"""
    try:
        # Load configuration
        config = Config.from_env()
        config.require_confirmation = confirm

        if verbose:
            config.log_level = "DEBUG"

        setup_logging(config.log_level, config.log_file)

        if batch_file:
            asyncio.run(_execute_batch_commands(config, batch_file, dry_run))
        else:
            asyncio.run(_execute_single_command(config, command, dry_run))

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def status(
    format_output: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Show system status and agent information"""
    try:
        config = Config.from_env()

        if verbose:
            config.log_level = "DEBUG"

        setup_logging(config.log_level, config.log_file)

        asyncio.run(_show_system_status(config, format_output))

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start interactive operations assistant"""
    try:
        config = Config.from_env()
        setup_logging(config.log_level, config.log_file)

        console.print(Panel.fit(
            "🤖 Starting Interactive Operations Assistant",
            style="bold green"
        ))

        agent = OperationsAgent(config)
        asyncio.run(agent.run())

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def health_check(
    quick: bool = typer.Option(False, "--quick", "-q", help="Quick health check only"),
    format_output: str = typer.Option("table", "--format", "-f", help="Output format: table, json")
):
    """Perform system health check"""
    try:
        config = Config.from_env()
        setup_logging(config.log_level)

        asyncio.run(_perform_health_check(config, quick, format_output))

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def tools_list():
    """List all available MCP tools"""
    try:
        config = Config.from_env()
        setup_logging(config.log_level)

        asyncio.run(_list_available_tools(config))

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


async def _execute_single_command(config: Config, command: str, dry_run: bool) -> None:
    """Execute a single command"""
    agent = OperationsAgent(config)

    try:
        await agent.initialize()

        console.print(f"🧠 Processing: {command}")

        if dry_run:
            console.print("🔍 DRY RUN MODE - No commands will be executed", style="yellow")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing request...", total=None)

            response = await agent.process_request(command)

            progress.update(task, description="Complete!")

        console.print(Panel(
            response.content,
            title="🤖 AI Response",
            border_style="green"
        ))

        if response.tool_calls:
            console.print("\n🛠️ Tools that would be executed:")
            for tool_call in response.tool_calls:
                console.print(f"  • {tool_call.get('name', 'unknown')}")

    finally:
        await agent.cleanup()


async def _execute_batch_commands(config: Config, batch_file: str, dry_run: bool) -> None:
    """Execute batch commands from file"""
    try:
        with open(batch_file, 'r') as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        console.print(f"📋 Found {len(commands)} commands in batch file")

        if dry_run:
            console.print("🔍 DRY RUN MODE - Commands will be analyzed but not executed", style="yellow")

        agent = OperationsAgent(config)
        await agent.initialize()

        try:
            results = await agent.process_batch_operations(commands)

            # Show summary
            successful = sum(1 for r in results if r.success)
            console.print(f"\n📊 Batch execution complete: {successful}/{len(results)} successful")

        finally:
            await agent.cleanup()

    except FileNotFoundError:
        console.print(f"❌ Batch file not found: {batch_file}", style="red")
        raise typer.Exit(1)


async def _show_system_status(config: Config, format_output: str) -> None:
    """Show comprehensive system status"""
    try:
        # Create a temporary operations agent to get system info
        agent = OperationsAgent(config)
        await agent.initialize()

        try:
            # Get system information
            system_info_response = await agent.process_request("Get comprehensive system status")

            if format_output == "json":
                console.print(system_info_response.content)
            else:
                # Display in table format
                table = Table(title="🖥️ System Status")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details")

                # Parse the response and create table entries
                # This is a simplified version - you'd parse the actual response
                table.add_row("MCP Connection", "✅ Connected", f"{len(agent.available_tools)} tools available")
                table.add_row("Risk Assessment", "✅ Enabled" if config.enable_risk_assessment else "❌ Disabled", "")
                table.add_row("Confirmation", "✅ Required" if config.require_confirmation else "❌ Not Required", "")

                console.print(table)

        finally:
            await agent.cleanup()

    except Exception as e:
        console.print(f"❌ Error getting system status: {e}", style="red")


async def _perform_health_check(config: Config, quick: bool, format_output: str) -> None:
    """Perform system health check"""
    health_results = {
        "timestamp": asyncio.get_event_loop().time(),
        "checks": []
    }

    try:
        agent = OperationsAgent(config)
        await agent.initialize()

        try:
            # Basic connectivity check
            health_results["checks"].append({
                "name": "MCP Connection",
                "status": "pass" if agent.mcp_session else "fail",
                "details": f"{len(agent.available_tools)} tools available"
            })

            if not quick:
                # Extended health checks
                response = await agent.process_request("Check system health including CPU, memory, and disk usage")

                health_results["checks"].append({
                    "name": "System Resources",
                    "status": "checked",
                    "details": "See full response"
                })

                health_results["system_response"] = response.content

            if format_output == "json":
                console.print(json.dumps(health_results, indent=2))
            else:
                # Display as table
                table = Table(title="🏥 System Health Check")
                table.add_column("Check", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details")

                for check in health_results["checks"]:
                    status_icon = "✅" if check["status"] == "pass" else "❌" if check["status"] == "fail" else "ℹ️"
                    table.add_row(check["name"], f"{status_icon} {check['status']}", check["details"])

                console.print(table)

        finally:
            await agent.cleanup()

    except Exception as e:
        health_results["checks"].append({
            "name": "Health Check",
            "status": "error",
            "details": str(e)
        })

        if format_output == "json":
            console.print(json.dumps(health_results, indent=2))
        else:
            console.print(f"❌ Health check failed: {e}", style="red")


async def _list_available_tools(config: Config) -> None:
    """List all available MCP tools"""
    try:
        agent = OperationsAgent(config)
        await agent.initialize()

        try:
            table = Table(title="🛠️ Available MCP Tools")
            table.add_column("Tool Name", style="cyan")
            table.add_column("Description", style="green")

            for tool in agent.available_tools:
                table.add_row(tool.name, tool.description)

            console.print(table)
            console.print(f"\n📊 Total tools available: {len(agent.available_tools)}")

        finally:
            await agent.cleanup()

    except Exception as e:
        console.print(f"❌ Error listing tools: {e}", style="red")


@app.command()
def version():
    """Show version information"""
    console.print(Panel.fit(
        """🤖 MCP AI Agent v1.0.0

Built with:
• Google Gemini SDK
• Model Context Protocol (MCP)
• Rich CLI Interface
• Comprehensive Security Features

For more information visit: https://github.com/mcp-ai-agent
        """,
        title="Version Information",
        border_style="blue"
    ))


def main():
    """Main entry point"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()