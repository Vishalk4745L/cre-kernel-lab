"""
Adapter Registry — Kernel-side Adapter Manager

This layer allows:
- Dynamic agent registration
- Hot-plug adapters (future)
- Zero kernel changes when adapters increase

Kernel talks ONLY to this registry.
"""

from typing import Dict, List, Optional

from kernel.core.adapter_interface import AgentAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        # adapter_id -> adapter instance
        self._adapters: Dict[str, AgentAdapter] = {}

    def register(self, adapter: AgentAdapter) -> None:
        """
        Register a new adapter.

        Called during:
        - startup
        - hot-load (future)
        """
        if not getattr(adapter, "adapter_id", None):
            raise ValueError("Adapter must define a non-empty adapter_id")
        self._adapters[adapter.adapter_id] = adapter

    def get(self, adapter_id: str) -> Optional[AgentAdapter]:
        """
        Fetch adapter by ID.
        Kernel routing depends on this.
        """
        return self._adapters.get(adapter_id)

    def list(self) -> List[str]:
        """
        List all available adapters.
        Useful for:
        - debugging
        - UI
        - governance
        """
        return list(self._adapters.keys())
