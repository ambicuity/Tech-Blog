from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    name: str
    version: str
    status: str
    confidence: float
    artifacts: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class GateResult:
    name: str
    passed: bool
    score: float
    threshold: float
    critical_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PublishDecision:
    outcome: str
    confidence: float
    requires_sampling_review: bool
    reason: str
