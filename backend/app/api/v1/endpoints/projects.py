"""Tenant-scoped CRUD endpoints for projects, locations, and keywords."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_context, get_current_user, get_owned_project_or_404
from app.db.session import get_db_session
from app.models.keyword import Keyword
from app.models.project import Project
from app.models.target_location import TargetLocation
from app.models.user import User
from app.organizations.models import OrganizationMembership
from app.schemas.keyword import KeywordCreateRequest, KeywordResponse, KeywordUpdateRequest
from app.schemas.location import LocationCreateRequest, LocationResponse, LocationUpdateRequest
from app.schemas.project import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest
from app.utils.text import slugify


router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[ProjectResponse]:
    """Return all projects owned by the authenticated user."""
    statement = select(Project).where(Project.owner_id == current_user.id).order_by(Project.created_at)
    projects = (await db_session.scalars(statement)).all()
    return [ProjectResponse.model_validate(project) for project in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProjectResponse:
    """Create a new project for the authenticated user."""
    slug = slugify(payload.slug or payload.name)
    existing_project = await db_session.scalar(
        select(Project).where(Project.owner_id == current_user.id, Project.slug == slug)
    )
    if existing_project is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project with this slug already exists.",
        )

    project = Project(
        owner_id=current_user.id,
        name=payload.name.strip(),
        slug=slug,
        description=payload.description.strip() if payload.description else None,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProjectResponse:
    """Return one owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProjectResponse:
    """Update one owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)

    if payload.name is not None:
        project.name = payload.name.strip()

    if payload.slug is not None:
        slug = slugify(payload.slug)
        existing_project = await db_session.scalar(
            select(Project).where(
                Project.owner_id == current_user.id,
                Project.slug == slug,
                Project.id != project.id,
            )
        )
        if existing_project is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A project with this slug already exists.",
            )
        project.slug = slug

    if payload.description is not None:
        project.description = payload.description.strip() or None

    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete one owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    await db_session.delete(project)
    await db_session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{project_id}/locations", response_model=list[LocationResponse])
async def list_locations(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[LocationResponse]:
    """Return all locations under one owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    statement = select(TargetLocation).where(TargetLocation.project_id == project.id)
    locations = (await db_session.scalars(statement)).all()
    return [LocationResponse.model_validate(location) for location in locations]


@router.post(
    "/{project_id}/locations",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_location(
    project_id: UUID,
    payload: LocationCreateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> LocationResponse:
    """Create a new location for an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    location = TargetLocation(project_id=project.id, **payload.model_dump())
    db_session.add(location)
    await db_session.commit()
    await db_session.refresh(location)
    return LocationResponse.model_validate(location)


@router.get("/{project_id}/locations/{location_id}", response_model=LocationResponse)
async def get_location(
    project_id: UUID,
    location_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> LocationResponse:
    """Return one location under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    location = await db_session.scalar(
        select(TargetLocation).where(
            TargetLocation.id == location_id,
            TargetLocation.project_id == project.id,
        )
    )
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location was not found.")
    return LocationResponse.model_validate(location)


@router.put("/{project_id}/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    project_id: UUID,
    location_id: UUID,
    payload: LocationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> LocationResponse:
    """Update one location under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    location = await db_session.scalar(
        select(TargetLocation).where(
            TargetLocation.id == location_id,
            TargetLocation.project_id == project.id,
        )
    )
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location was not found.")

    for field_name, field_value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field_name, field_value)

    db_session.add(location)
    await db_session.commit()
    await db_session.refresh(location)
    return LocationResponse.model_validate(location)


@router.delete("/{project_id}/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    project_id: UUID,
    location_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete one location under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    location = await db_session.scalar(
        select(TargetLocation).where(
            TargetLocation.id == location_id,
            TargetLocation.project_id == project.id,
        )
    )
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location was not found.")

    await db_session.delete(location)
    await db_session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{project_id}/keywords", response_model=list[KeywordResponse])
async def list_keywords(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[KeywordResponse]:
    """Return all keywords under one owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    statement = select(Keyword).where(Keyword.project_id == project.id).order_by(Keyword.created_at)
    keywords = (await db_session.scalars(statement)).all()
    return [KeywordResponse.model_validate(keyword) for keyword in keywords]


@router.post(
    "/{project_id}/keywords",
    response_model=KeywordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_keyword(
    project_id: UUID,
    payload: KeywordCreateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> KeywordResponse:
    """Create a new keyword under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    location = await db_session.scalar(
        select(TargetLocation).where(
            TargetLocation.id == payload.target_location_id,
            TargetLocation.project_id == project.id,
        )
    )
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target location does not belong to this project.",
        )

    # Enforce org-level keyword_limit: count all keywords across the user's projects.
    from app.organizations.models import Organization
    membership = await db_session.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.is_pending.is_(False),
        )
        .order_by(OrganizationMembership.created_at)
        .limit(1)
    )
    if membership is not None:
        org = await db_session.get(Organization, membership.organization_id)
        if org is not None and org.keyword_limit is not None:
            owned_project_ids = (
                await db_session.scalars(
                    select(Project.id).where(Project.owner_id == current_user.id)
                )
            ).all()
            total_keywords = await db_session.scalar(
                select(func.count(Keyword.id)).where(
                    Keyword.project_id.in_(owned_project_ids)
                )
            )
            if (total_keywords or 0) >= org.keyword_limit:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Keyword limit of {org.keyword_limit} reached. Upgrade your plan to track more keywords.",
                )

    keyword = Keyword(project_id=project.id, **payload.model_dump())
    db_session.add(keyword)
    await db_session.commit()
    await db_session.refresh(keyword)
    return KeywordResponse.model_validate(keyword)


@router.get("/{project_id}/keywords/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    project_id: UUID,
    keyword_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> KeywordResponse:
    """Return one keyword under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    keyword = await db_session.scalar(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.project_id == project.id,
        )
    )
    if keyword is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword was not found.")
    return KeywordResponse.model_validate(keyword)


@router.put("/{project_id}/keywords/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    project_id: UUID,
    keyword_id: UUID,
    payload: KeywordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> KeywordResponse:
    """Update one keyword under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    keyword = await db_session.scalar(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.project_id == project.id,
        )
    )
    if keyword is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword was not found.")

    changes = payload.model_dump(exclude_unset=True)
    target_location_id = changes.get("target_location_id")
    if target_location_id is not None:
        location = await db_session.scalar(
            select(TargetLocation).where(
                TargetLocation.id == target_location_id,
                TargetLocation.project_id == project.id,
            )
        )
        if location is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target location does not belong to this project.",
            )

    for field_name, field_value in changes.items():
        setattr(keyword, field_name, field_value)

    db_session.add(keyword)
    await db_session.commit()
    await db_session.refresh(keyword)
    return KeywordResponse.model_validate(keyword)


@router.delete("/{project_id}/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    project_id: UUID,
    keyword_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete one keyword under an owned project."""
    project = await get_owned_project_or_404(project_id, current_user, db_session)
    keyword = await db_session.scalar(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.project_id == project.id,
        )
    )
    if keyword is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword was not found.")

    await db_session.delete(keyword)
    await db_session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
