"""Import ORM models so SQLAlchemy metadata is fully registered."""

from app.google.models import GoogleAccount, GoogleBusinessProfile
from app.models.agency import AgencyBranding, AgencyClientLink
from app.models.audit import AuditReport
from app.models.automation import AutomationRule
from app.models.heatmap_run import HeatmapRun
from app.models.keyword import Keyword
from app.models.post import GBPPost
from app.models.project import Project
from app.models.ranking_history import RankingHistory
from app.models.review import GBPReview
from app.models.target_location import TargetLocation
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership

__all__ = [
    "AgencyBranding",
    "AgencyClientLink",
    "AuditReport",
    "AutomationRule",
    "GBPPost",
    "GBPReview",
    "GoogleAccount",
    "GoogleBusinessProfile",
    "HeatmapRun",
    "Keyword",
    "Organization",
    "OrganizationMembership",
    "Project",
    "RankingHistory",
    "TargetLocation",
    "User",
]
