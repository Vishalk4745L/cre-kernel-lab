"""
Adapter Registry — Kernel-side Adapter Manager

This layer allows:
- Dynamic agent registration
- Hot-plug adapters (future)
- Zero kernel changes when adapters increase

Kernel talks ONLY to this registry.
"""

from typing import Dict


class AdapterRegistry:
    def __init__(self):
        # adapter_id -> adapter instance
        self._adapters: Dict[str, object] = {}

    def register(self, adapter):
        """
        Register a new adapter.

        Called during:
        - startup
        - hot-load (future)
        """
        self._adapters[adapter.adapter_id] = adapter

    def get(self, adapter_id: str):
        """
        Fetch adapter by ID.
        Kernel routing depends on this.
        """
        return self._adapters.get(adapter_id)

    def list(self):
        """
        List all available adapters.
        Useful for:
        - debugging
        - UI
        - governance
        """
        return list(self._adapters.keys())