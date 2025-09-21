"""
MCP AI Agent Base Class with Gemini API Integration
Provides unified interface for Gemini API and MCP server communication
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from pydantic import BaseModel, Field

from ..security.risk_assessor import RiskAssessor
from ..utils.config import Config


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]


class AIResponse(BaseModel):
    """AI Response model"""
    content: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.0)
    risk_level: str = Field(default="low")


class BaseMCPAgent(ABC):
    """
    Base class for MCP AI Agents with Gemini API integration
    Provides core functionality for AI-powered system operations
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.risk_assessor = RiskAssessor(config)
        self.mcp_session: Optional[ClientSession] = None
        self.available_tools: List[MCPTool] = []

        # Initialize Gemini
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)

    async def initialize(self) -> None:
        """Initialize MCP connection and load available tools"""
        try:
            # Connect to MCP server
            server_params = StdioServerParameters(
                command=["python", "-m", "mcp_ai_agent.mcp.server"],
                env=None
            )

            self.mcp_session = ClientSession(server_params)
            await self.mcp_session.__aenter__()

            # Load available tools
            await self._load_tools()

            self.logger.info(f"Initialized {self.__class__.__name__} with {len(self.available_tools)} tools")

        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            raise

    async def _load_tools(self) -> None:
        """Load available MCP tools"""
        try:
            if not self.mcp_session:
                raise RuntimeError("MCP session not initialized")

            # Get tools from MCP server
            tools_response = await self.mcp_session.list_tools()

            for tool in tools_response.tools:
                mcp_tool = MCPTool(
                    name=tool.name,
                    description=tool.description or "",
                    parameters=tool.inputSchema or {}
                )
                self.available_tools.append(mcp_tool)

        except Exception as e:
            self.logger.error(f"Failed to load tools: {e}")
            raise

    async def process_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """
        Process user request using AI and execute appropriate tools

        Args:
            user_input: Natural language request from user
            context: Additional context for processing

        Returns:
            AIResponse with content and tool execution results
        """
        try:
            # Prepare system prompt with available tools
            system_prompt = self._build_system_prompt()

            # Build full prompt
            full_prompt = f"{system_prompt}\n\nUser Request: {user_input}"
            if context:
                full_prompt += f"\nContext: {json.dumps(context, indent=2)}"

            # Get AI response
            response = await self._generate_response(full_prompt)

            # Parse and validate response
            ai_response = self._parse_ai_response(response)

            # Execute tools if requested
            if ai_response.tool_calls:
                tool_results = await self._execute_tools(ai_response.tool_calls)
                ai_response.content += f"\n\nTool Results:\n{tool_results}"

            return ai_response

        except Exception as e:
            self.logger.error(f"Failed to process request: {e}")
            return AIResponse(
                content=f"Error processing request: {str(e)}",
                confidence=0.0,
                risk_level="high"
            )

    def _build_system_prompt(self) -> str:
        """Build system prompt with available tools"""
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.available_tools
        ])

        return f"""You are an intelligent system administration assistant with access to MCP tools.
Available tools:
{tools_desc}

You can execute system operations safely and efficiently. Always:
1. Assess the risk level of operations (low/medium/high)
2. Provide clear explanations of what you're doing
3. Use appropriate tools for the task
4. Include confidence scores in your responses

Respond in JSON format with:
{{
    "content": "Your response explanation",
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

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text

        except Exception as e:
            self.logger.error(f"Failed to generate AI response: {e}")
            raise

    def _parse_ai_response(self, response_text: str) -> AIResponse:
        """Parse AI response text into structured format"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                response_data = json.loads(response_text)
                return AIResponse(**response_data)
            else:
                # Fallback to plain text response
                return AIResponse(
                    content=response_text,
                    confidence=0.8,
                    risk_level="low"
                )

        except json.JSONDecodeError:
            # If JSON parsing fails, treat as plain text
            return AIResponse(
                content=response_text,
                confidence=0.7,
                risk_level="medium"
            )

    async def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> str:
        """Execute MCP tools based on AI response"""
        results = []

        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})

                # Risk assessment
                risk_level = await self.risk_assessor.assess_tool_call(tool_name, arguments)

                # Check if confirmation required
                if risk_level in ["medium", "high"] and self.config.require_confirmation:
                    confirmation = await self._request_confirmation(tool_name, arguments, risk_level)
                    if not confirmation:
                        results.append(f"Tool {tool_name} execution cancelled by user")
                        continue

                # Execute tool
                if self.mcp_session:
                    result = await self.mcp_session.call_tool(tool_name, arguments)
                    results.append(f"{tool_name}: {result.content}")
                else:
                    results.append(f"Error: MCP session not available")

            except Exception as e:
                self.logger.error(f"Failed to execute tool {tool_name}: {e}")
                results.append(f"Error executing {tool_name}: {str(e)}")

        return "\n".join(results)

    async def _request_confirmation(self, tool_name: str, arguments: Dict[str, Any], risk_level: str) -> bool:
        """Request user confirmation for risky operations"""
        # In CLI mode, this would prompt the user
        # For now, implement as a simple check
        return True  # Override in subclasses for interactive confirmation

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)

    @abstractmethod
    async def run(self) -> None:
        """Main execution method - implement in subclasses"""
        pass