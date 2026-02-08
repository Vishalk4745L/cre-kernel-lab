"""
CRE Kernel Core
================

This is the HEART of the system.

IMPORTANT DESIGN RULES:
- Kernel does NOT know about Gemini
- Kernel does NOT know about MCP
- Kernel does NOT know about A2A
- Kernel does NOT know about SDKs

Kernel ONLY:
- Registers adapters
- Routes messages
- Enforces structure

Future adapters plug in WITHOUT modifying this file.
"""

from typing import Dict

from kernel.core.adapter_interface import AgentAdapter
from kernel.core.adapter_registry import AdapterRegistry


class Kernel:
    """
    Central Kernel Brain (v1)

    Stable + minimal.
    This file should change VERY RARELY.
    """

    def __init__(self) -> None:
        # Holds all registered adapters
        self.registry = AdapterRegistry()

    def register_adapter(self, adapter: AgentAdapter) -> None:
        """
        Attach an adapter to the kernel.

        Adapter can be:
        - Mock agent
        - Gemini agent
        - MCP agent
        - A2A agent
        - Any future SDK
        """
        self.registry.register(adapter)

    def route(self, adapter_id: str, message: Dict) -> Dict:
        """
        Route a message to a specific adapter.

        message MUST be canonical KernelMessage dict.
        """
        adapter = self.registry.get(adapter_id)

        if not adapter:
            raise ValueError(f"Adapter not found: {adapter_id}")

        return adapter.send(message)
