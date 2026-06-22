"""Automation rule schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AutomationRuleCreateRequest(BaseModel):
    rule_type: str = Field(
        ...,
        pattern="^(auto_reply_positive|auto_reply_neutral|auto_reply_negative|scheduled_post)$",
    )
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True
    config: dict[str, Any] | None = None


class AutomationRuleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None
    config: dict[str, Any] | None = None


class AutomationRuleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    rule_type: str
    name: str
    description: str | None
    is_active: bool
    config: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
