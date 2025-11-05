from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass
class SubscriptionEvent:
    provider: str
    external_id: str
    type: str  # created/renewed/canceled/failed
    payload: dict

class SubscriptionProvider(Protocol):
    async def verify(self, headers: dict, body: bytes) -> bool: ...
    async def parse(self, body: bytes) -> SubscriptionEvent: ...
