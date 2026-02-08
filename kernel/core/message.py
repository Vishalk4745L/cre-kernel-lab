"""
Canonical Kernel Message
========================

This is the ONLY message format allowed inside the Kernel.

Why this exists:
- Prevent context rot
- Prevent prompt poisoning
- Prevent adapter chaos
- Enforce structure forever

ALL adapters (Gemini / MCP / A2A / SDKs)
must translate TO and FROM this format.
"""

from dataclasses import dataclass
from typing import Any, Dict
import time


@dataclass
class KernelMessage:
    source: str            # who sent this (agent / tool / human)
    type: str              # thought | action | result | signal
    content: Any           # payload
    confidence: float      # 0.0 → 1.0
    timestamp: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "type": self.type,
            "content": self.content,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }