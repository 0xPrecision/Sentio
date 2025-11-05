from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, TypedDict, Any

EventType = Literal["created", "renewed", "canceled", "failed"]

@dataclass
class StarsEvent:
    provider: str
    external_id: str
    type: EventType
    tenant_slug: str | None
    raw: dict

# TODO(api): Replace with actual Telegram Stars webhook payload once stable.
class StarsWebhookPayload(TypedDict, total=False):
    event: str
    subscription_id: str
    invoice_id: str
    tenant_slug: str
    data: dict[str, Any]
