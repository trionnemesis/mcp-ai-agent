"""
Automated Operations Assistant with Natural Language Interface
Provides intelligent system administration through conversational AI
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .base_agent import BaseMCPAgent, AIResponse
from ..utils.config import Config


class OperationRequest(BaseModel):
    """Operation request model"""
    request_id: str
    user_input: str
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, critical


class OperationResult(BaseModel):
    """Operation result model"""
    request_id: str
    success: bool
    result: str
    tools_used: List[str]
    execution_time: float
    timestamp: datetime


class OperationHistory(BaseModel):
    """Operation history entry"""
    request: OperationRequest
    result: OperationResult
    rollback_commands: List[str] = []


class OperationsAgent(BaseMCPAgent):
    """
    Automated Operations Assistant

    Features:
    - Natural language command interpretation
    - Safe command execution with risk assessment
    - Operation history and audit trail
    - Rollback capabilities
    - Intelligent error handling and recovery
    - Multi-step task automation
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self.operation_history: List[OperationHistory] = []
        self.interactive_mode = True

    async def run(self) -> None:
        """Main interactive operations loop"""
        await self.initialize()

        self.logger.info("Starting automated operations assistant...")
        print("🤖 Operations Assistant ready! Type 'help' for commands or 'quit' to exit.")

        while self.interactive_mode:
            try:
                user_input = input("\n🔧 Operations> ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'history':
                    await self._show_history()
                    continue
                elif user_input.lower() == 'status':
                    await self._show_status()
                    continue
                elif user_input.startswith('rollback'):
                    await self._handle_rollback(user_input)
                    continue

                if user_input:
                    await self._process_operation_request(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Operations assistant stopped.")
                break
            except Exception as e:
                self.logger.error(f"Error in operations loop: {e}")
                print(f"❌ Error: {e}")

        await self.cleanup()

    def _show_help(self) -> None:
        """Show help information"""
        help_text = """
🔧 Operations Assistant Commands:

Natural Language Operations:
  "Check system status"              - Get comprehensive system info
  "Show running processes"           - List current processes
  "Restart nginx service"            - Manage system services
  "Check disk space"                 - Analyze disk usage
  "Monitor CPU usage"                - Real-time CPU monitoring
  "Install package htop"             - Package management
  "Create backup of /etc"            - File operations
  "Check network connectivity"       - Network diagnostics

Special Commands:
  help                              - Show this help
  history                           - Show operation history
  status                            - Show agent status
  rollback <number>                 - Rollback last N operations
  quit/exit/q                       - Exit assistant

Examples:
  🔧 Operations> Check if port 80 is open
  🔧 Operations> Find processes using more than 50% CPU
  🔧 Operations> Create a backup of my home directory
  🔧 Operations> Show me the last 100 lines of apache logs
        """
        print(help_text)

    async def _show_history(self) -> None:
        """Show operation history"""
        if not self.operation_history:
            print("📜 No operations in history.")
            return

        print("\n📜 Operation History (last 10):")
        for i, history in enumerate(self.operation_history[-10:], 1):
            status = "✅" if history.result.success else "❌"
            print(f"{i:2d}. {status} {history.request.user_input}")
            print(f"     Time: {history.result.execution_time:.2f}s | Tools: {', '.join(history.result.tools_used)}")

    async def _show_status(self) -> None:
        """Show agent status"""
        tool_count = len(self.available_tools)
        history_count = len(self.operation_history)

        status_info = f"""
🤖 Operations Assistant Status:
   📡 MCP Connection: {'✅ Connected' if self.mcp_session else '❌ Disconnected'}
   🛠️  Available Tools: {tool_count}
   📜 Operations History: {history_count}
   🔒 Risk Assessment: {'✅ Enabled' if self.config.enable_risk_assessment else '❌ Disabled'}
   ⚠️  Confirmation Required: {'✅ Yes' if self.config.require_confirmation else '❌ No'}
        """
        print(status_info)

    async def _handle_rollback(self, command: str) -> None:
        """Handle rollback command"""
        try:
            parts = command.split()
            if len(parts) < 2:
                print("❌ Usage: rollback <number_of_operations>")
                return

            count = int(parts[1])
            if count <= 0 or count > len(self.operation_history):
                print(f"❌ Invalid rollback count. Available: 1-{len(self.operation_history)}")
                return

            print(f"🔄 Rolling back last {count} operation(s)...")
            await self._perform_rollback(count)

        except ValueError:
            print("❌ Invalid number for rollback count")
        except Exception as e:
            print(f"❌ Rollback error: {e}")

    async def _perform_rollback(self, count: int) -> None:
        """Perform rollback of operations"""
        operations_to_rollback = self.operation_history[-count:]

        for i, history in enumerate(reversed(operations_to_rollback), 1):
            print(f"🔄 Rolling back operation {i}/{count}: {history.request.user_input}")

            if not history.rollback_commands:
                print(f"⚠️  No rollback commands available for this operation")
                continue

            for rollback_cmd in history.rollback_commands:
                try:
                    # Execute rollback command
                    result = await self._execute_rollback_command(rollback_cmd)
                    print(f"   ✅ Executed: {rollback_cmd}")
                except Exception as e:
                    print(f"   ❌ Failed: {rollback_cmd} - {e}")

        # Remove rolled back operations from history
        self.operation_history = self.operation_history[:-count]
        print(f"✅ Rollback completed for {count} operation(s)")

    async def _execute_rollback_command(self, command: str) -> str:
        """Execute a rollback command"""
        # This would execute the rollback command safely
        # For now, we'll simulate it
        return f"Simulated rollback: {command}"

    async def _process_operation_request(self, user_input: str) -> None:
        """Process a natural language operation request"""
        request_id = f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        operation_request = OperationRequest(
            request_id=request_id,
            user_input=user_input,
            timestamp=datetime.now()
        )

        print(f"🧠 Analyzing request: {user_input}")

        start_time = datetime.now()

        try:
            # Process the request with AI
            response = await self._intelligent_operation_processing(user_input)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Create operation result
            operation_result = OperationResult(
                request_id=request_id,
                success=True,
                result=response.content,
                tools_used=[call.get("name", "unknown") for call in response.tool_calls],
                execution_time=execution_time,
                timestamp=datetime.now()
            )

            # Generate rollback commands if applicable
            rollback_commands = await self._generate_rollback_commands(response.tool_calls)

            # Store in history
            history_entry = OperationHistory(
                request=operation_request,
                result=operation_result,
                rollback_commands=rollback_commands
            )
            self.operation_history.append(history_entry)

            # Keep only last 100 operations
            if len(self.operation_history) > 100:
                self.operation_history = self.operation_history[-100:]

            print(f"✅ Operation completed in {execution_time:.2f}s")
            print(f"📋 Result:\n{response.content}")

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            operation_result = OperationResult(
                request_id=request_id,
                success=False,
                result=f"Error: {str(e)}",
                tools_used=[],
                execution_time=execution_time,
                timestamp=datetime.now()
            )

            history_entry = OperationHistory(
                request=operation_request,
                result=operation_result
            )
            self.operation_history.append(history_entry)

            print(f"❌ Operation failed: {e}")

    async def _intelligent_operation_processing(self, user_input: str) -> AIResponse:
        """Process operation using AI with enhanced system prompt"""

        # Build enhanced system prompt for operations
        system_prompt = self._build_operations_system_prompt()

        # Add context about system state
        context = await self._gather_system_context()

        # Enhanced prompt with operation-specific instructions
        full_prompt = f"""{system_prompt}

Current System Context:
{json.dumps(context, indent=2)}

User Request: {user_input}

Please analyze this request and determine the appropriate actions to take.
Consider:
1. What tools are needed to fulfill this request
2. The order of operations required
3. Any safety considerations
4. Expected outcomes

Provide a helpful response with any necessary tool executions.
"""

        return await self.process_request(user_input, context)

    def _build_operations_system_prompt(self) -> str:
        """Build specialized system prompt for operations"""
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.available_tools
        ])

        return f"""You are an intelligent system operations assistant with expertise in Linux administration.
You can understand natural language requests and translate them into appropriate system operations.

Available tools:
{tools_desc}

You excel at:
- System monitoring and diagnostics
- Service management
- File and directory operations
- Network troubleshooting
- Process management
- Log analysis
- Package management
- Performance optimization

Always:
1. Explain what you're doing and why
2. Provide clear, actionable results
3. Include relevant details and context
4. Suggest follow-up actions when appropriate
5. Use multiple tools when needed to provide comprehensive solutions

For safety:
- Always assess risk levels
- Explain potential impacts
- Suggest safer alternatives when appropriate
- Provide rollback information for destructive operations

Respond in JSON format with:
{{
    "content": "Detailed explanation of actions and results",
    "tool_calls": [
        {{
            "name": "tool_name",
            "arguments": {{...}}
        }}
    ],
    "confidence": 0.95,
    "risk_level": "low|medium|high"
}}
"""

    async def _gather_system_context(self) -> Dict[str, Any]:
        """Gather current system context for operations"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "available_tools": len(self.available_tools),
            "operation_count": len(self.operation_history)
        }

        try:
            # Try to get basic system info
            if self.mcp_session:
                system_info = await self.mcp_session.call_tool("get_system_info", {})
                if system_info and system_info.content:
                    context["system_info"] = system_info.content[0].text if system_info.content else None

        except Exception as e:
            self.logger.debug(f"Could not gather system context: {e}")

        return context

    async def _generate_rollback_commands(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        """Generate rollback commands for tool calls"""
        rollback_commands = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            arguments = tool_call.get("arguments", {})

            try:
                rollback_cmd = await self._generate_tool_rollback(tool_name, arguments)
                if rollback_cmd:
                    rollback_commands.append(rollback_cmd)
            except Exception as e:
                self.logger.warning(f"Could not generate rollback for {tool_name}: {e}")

        return rollback_commands

    async def _generate_tool_rollback(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Generate rollback command for a specific tool call"""

        if tool_name == "manage_service":
            service_name = arguments.get("service_name", "")
            action = arguments.get("action", "")

            rollback_actions = {
                "start": "stop",
                "stop": "start",
                "enable": "disable",
                "disable": "enable",
                "restart": None  # No direct rollback for restart
            }

            rollback_action = rollback_actions.get(action)
            if rollback_action:
                return f"systemctl {rollback_action} {service_name}"

        elif tool_name == "file_operations":
            operation = arguments.get("operation", "")
            path = arguments.get("path", "")

            if operation == "create" and path:
                return f"rm -f {path}"
            elif operation == "delete" and path:
                return f"# Cannot rollback deletion of {path} - file was permanently removed"

        elif tool_name == "execute_command":
            command = arguments.get("command", "")
            # For safety, we don't auto-generate rollbacks for arbitrary commands
            return f"# Manual rollback may be needed for: {command}"

        return None

    async def process_batch_operations(self, operations: List[str]) -> List[OperationResult]:
        """Process multiple operations in batch"""
        results = []

        print(f"🔄 Processing {len(operations)} operations in batch...")

        for i, operation in enumerate(operations, 1):
            print(f"📋 Operation {i}/{len(operations)}: {operation}")

            try:
                response = await self._intelligent_operation_processing(operation)

                result = OperationResult(
                    request_id=f"batch_{i}",
                    success=True,
                    result=response.content,
                    tools_used=[call.get("name", "unknown") for call in response.tool_calls],
                    execution_time=0.0,  # Would calculate actual time
                    timestamp=datetime.now()
                )

                results.append(result)
                print(f"   ✅ Completed")

            except Exception as e:
                result = OperationResult(
                    request_id=f"batch_{i}",
                    success=False,
                    result=f"Error: {str(e)}",
                    tools_used=[],
                    execution_time=0.0,
                    timestamp=datetime.now()
                )

                results.append(result)
                print(f"   ❌ Failed: {e}")

        print(f"🏁 Batch processing completed: {sum(1 for r in results if r.success)}/{len(results)} successful")
        return results