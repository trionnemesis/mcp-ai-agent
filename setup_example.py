#!/usr/bin/env python3
"""
MCP AI Agent Setup and Demo Script
Demonstrates the capabilities of the MCP AI Agent system
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.monitoring_agent import MonitoringAgent
from src.agents.operations_agent import OperationsAgent
from src.utils.config import Config


async def demo_monitoring_agent():
    """Demonstrate the monitoring agent capabilities"""
    print("🔍 Demonstrating Monitoring Agent...")

    # Create mock config for demo
    config = Config(
        gemini_api_key="demo_key",
        monitoring_interval=5,
        cpu_threshold=75.0,
        memory_threshold=80.0,
        disk_threshold=85.0
    )

    agent = MonitoringAgent(config)

    # Simulate monitoring status check
    print("📊 Getting monitoring status...")
    status = await agent.get_monitoring_status()
    print(f"Monitoring Status: {status}")

    print("✅ Monitoring agent demo completed")


async def demo_operations_agent():
    """Demonstrate the operations agent capabilities"""
    print("🛠️ Demonstrating Operations Agent...")

    config = Config(
        gemini_api_key="demo_key",
        enable_risk_assessment=True,
        require_confirmation=False  # Disable for demo
    )

    agent = OperationsAgent(config)

    # Simulate some operation requests
    demo_requests = [
        "Show system information",
        "List running processes",
        "Check disk usage",
        "Show network interfaces"
    ]

    print("📝 Processing demo requests...")
    for request in demo_requests:
        print(f"  🔄 Request: {request}")
        # In real scenario, this would process with AI
        print(f"  ✅ Simulated processing complete")

    print("✅ Operations agent demo completed")


async def setup_environment():
    """Setup the environment for MCP AI Agent"""
    print("⚙️ Setting up MCP AI Agent environment...")

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        return False

    print(f"✅ Python version: {sys.version}")

    # Check if required packages are installed
    required_packages = [
        'google.generativeai',
        'mcp',
        'psutil',
        'pydantic',
        'typer',
        'rich'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")

    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    # Check for Gemini API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY='your_api_key_here'")
    else:
        print("✅ GEMINI_API_KEY is set")

    print("✅ Environment setup completed")
    return True


def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples:")
    print("=" * 50)

    print("\n🖥️ CLI Commands:")
    print("mcp-agent interactive              # Start interactive mode")
    print("mcp-agent monitor                  # Start system monitoring")
    print("mcp-agent execute 'check system'  # Execute command")
    print("mcp-agent status                   # Show system status")
    print("mcp-agent health-check            # Perform health check")

    print("\n🤖 Natural Language Examples:")
    print("'Check system status'")
    print("'Restart nginx service'")
    print("'Show top 10 CPU consuming processes'")
    print("'Check disk space on all partitions'")
    print("'Find large files in /tmp directory'")

    print("\n⚠️ Security Features:")
    print("• Automatic risk assessment")
    print("• Confirmation for dangerous operations")
    print("• Operation history and rollback")
    print("• Audit trail logging")


def show_architecture():
    """Show system architecture"""
    print("\n🏗️ System Architecture:")
    print("=" * 50)

    architecture = """
    ┌─────────────────────────────────────────────────────────┐
    │                    MCP AI Agent                         │
    └─────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
    ┌───────────▼────┐ ┌────────▼────┐ ┌────────▼────────┐
    │ Monitoring     │ │ Operations  │ │ Security        │
    │ Agent          │ │ Agent       │ │ Assessor        │
    └───────┬────────┘ └────┬────────┘ └─────────────────┘
            │               │
    ┌───────▼────────┐     │
    │ AI Analysis    │     │
    │ & Alerting     │     │
    └────────────────┘     │
                           │
                ┌──────────▼──────────┐
                │    MCP Server       │
                │  (Linux Tools)      │
                └─────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼───┐         ┌────▼────┐        ┌────▼────┐
    │System │         │ Process │        │Network  │
    │ Info  │         │ Mgmt    │        │ Diag    │
    └───────┘         └─────────┘        └─────────┘
    """

    print(architecture)


async def main():
    """Main demo function"""
    print("🤖 MCP AI Agent Setup and Demo")
    print("=" * 50)

    # Setup environment
    if not await setup_environment():
        print("\n❌ Environment setup failed. Please install missing dependencies.")
        return

    # Show architecture
    show_architecture()

    # Show usage examples
    show_usage_examples()

    # Run demos
    print("\n🚀 Running Demos...")
    try:
        await demo_monitoring_agent()
        await demo_operations_agent()
    except Exception as e:
        print(f"⚠️ Demo error (expected without API key): {e}")

    print("\n✅ Setup and demo completed!")
    print("\n🚀 To get started:")
    print("1. Set your GEMINI_API_KEY environment variable")
    print("2. Run: mcp-agent interactive")
    print("3. Or try: mcp-agent execute 'check system status'")


if __name__ == "__main__":
    asyncio.run(main())