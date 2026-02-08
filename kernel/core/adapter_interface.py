"""
Adapter Interface — Kernel ↔ External Agent Contract (v1)

⚠️ CRITICAL DESIGN RULE:
Kernel must NEVER import Gemini / MCP / A2A / SDK directly.
Only Adapters are allowed to talk to the outside world.

This file is the STABILITY WALL.
Future protocols change → Kernel stays untouched.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class AgentAdapter(ABC):
    """
    Base class for ALL external agents.

    Examples:
    - Gemini 3 Flash adapter
    - MCP tool adapter
    - Google A2A adapter
    - Any future Agent SDK

    If something can "think / act / respond",
    it must obey this interface.
    """

    # Unique ID used by Kernel routing
    adapter_id: str

    # agent | tool | orchestrator | memory | verifier
    adapter_type: str

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """
        Declare what this adapter can do.

        Kernel uses this for:
        - routing
        - trust weighting
        - future auto-orchestration

        Example:
        {
            "reasoning": True,
            "planning": False,
            "confidence": 0.7
        }
        """
        pass

    @abstractmethod
    def send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core communication method.

        Input:
        - Canonical Kernel message (dict)
        Output:
        - Canonical response (dict)

        Adapter responsibility:
        - Translate Kernel message → external protocol
        - Call external API / agent
        - Translate response → Kernel format
        """
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Health check.

        Used for:
        - monitoring
        - failover
        - trust decay if adapter is unstable
        """
        pass