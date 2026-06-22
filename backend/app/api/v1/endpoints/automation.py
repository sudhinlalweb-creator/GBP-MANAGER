"""Automation rule CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context
from app.db.session import get_db_session
from app.models.automation import AutomationRule
from app.schemas.automation import (
    AutomationRuleCreateRequest,
    AutomationRuleResponse,
    AutomationRuleUpdateRequest,
)


router = APIRouter()


@router.get("", response_model=list[AutomationRuleResponse])
async def list_automation_rules(
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[AutomationRuleResponse]:
    """Return all automation rules for the active organization."""
    rules = (
        await db.scalars(
            select(AutomationRule)
            .where(AutomationRule.organization_id == context.organization.id)
            .order_by(AutomationRule.created_at)
        )
    ).all()
    return [AutomationRuleResponse.model_validate(r) for r in rules]


@router.post("", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(
    payload: AutomationRuleCreateRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> AutomationRuleResponse:
    """Create an automation rule for the active organization."""
    rule = AutomationRule(
        organization_id=context.organization.id,
        rule_type=payload.rule_type,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
        config=payload.config,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return AutomationRuleResponse.model_validate(rule)


@router.get("/{rule_id}", response_model=AutomationRuleResponse)
async def get_automation_rule(
    rule_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> AutomationRuleResponse:
    """Return one automation rule."""
    rule = await _get_rule_or_404(db, rule_id, context.organization.id)
    return AutomationRuleResponse.model_validate(rule)


@router.patch("/{rule_id}", response_model=AutomationRuleResponse)
async def update_automation_rule(
    rule_id: UUID,
    payload: AutomationRuleUpdateRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> AutomationRuleResponse:
    """Update an automation rule."""
    rule = await _get_rule_or_404(db, rule_id, context.organization.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return AutomationRuleResponse.model_validate(rule)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation_rule(
    rule_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete an automation rule."""
    rule = await _get_rule_or_404(db, rule_id, context.organization.id)
    await db.delete(rule)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _get_rule_or_404(
    db: AsyncSession, rule_id: UUID, org_id: UUID
) -> AutomationRule:
    rule = await db.scalar(
        select(AutomationRule).where(
            AutomationRule.id == rule_id,
            AutomationRule.organization_id == org_id,
        )
    )
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation rule not found.")
    return rule
