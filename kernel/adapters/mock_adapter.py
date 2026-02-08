"""
Mock Agent Adapter

Purpose:
- Safe test agent for Kernel ↔ Adapter contract
- No external dependency
- No LLM / API call
- Used for validating routing, trust, memory later

This file proves:
Kernel DOES NOT care who the agent is.
"""

from kernel.core.adapter_interface import AgentAdapter


class MockAgentAdapter(AgentAdapter):
    """
    Minimal Agent Adapter implementation (v1)

    Future:
    - Gemini Adapter
    - MCP Adapter
    - A2A Adapter
    - SDK-based Agent

    ALL of them must look like THIS to the Kernel.
    """

    adapter_id = "mock-agent"
    adapter_type = "agent"

    def capabilities(self) -> dict:
        """
        Describe what this agent can do.
        Kernel may use this in future for routing decisions.
        """
        return {
            "reasoning": True,
            "planning": False,
            "memory": False,
            "confidence": 0.42,
        }

    def send(self, message: dict) -> dict:
        """
        Kernel sends canonical message here.

        message schema:
        {
            source,
            type,
            content,
            confidence,
            timestamp
        }
        """

        return {
            "agent": self.adapter_id,
            "reply": f"Mock received: {message.get('content')}",
            "confidence": 0.42,
            "status": "ok",
        }

    def health(self) -> dict:
        """
        Kernel health check.
        Used in:
        - monitoring
        - orchestration
        - governance
        """
        return {
            "adapter": self.adapter_id,
            "status": "healthy",
        }
