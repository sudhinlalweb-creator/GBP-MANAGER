"""Prompt builders for the GBP AI audit engine."""

from __future__ import annotations

import json


def build_audit_system_prompt() -> str:
    """Return the system prompt for GBP audit analysis."""
    return (
        "You are a senior Local SEO specialist with deep expertise in Google Business Profile "
        "optimization. Your task is to analyze a GBP profile snapshot and produce a prioritized "
        "list of actionable recommendations.\n\n"
        "Rules:\n"
        "- Respond with valid JSON only. No markdown, no code fences, no explanation outside JSON.\n"
        "- Output format: {\"recommendations\": [...]}\n"
        "- Each recommendation must include: id (uuid4 string), priority (high|medium|low), "
        "category (completeness|reviews|photos|description|categories|qa|posts), "
        "title (max 80 chars), detail (1-3 sentences), impact_score (1-10 int), "
        "is_auto_fixable (bool), suggested_value (string or null), field_path (string or null).\n"
        "- Produce between 5 and 10 recommendations.\n"
        "- Prioritize by impact. High = critical gaps. Medium = significant improvements. "
        "Low = polish.\n"
        "- Never fabricate data. Only reference fields present in the snapshot.\n"
        "- is_auto_fixable should be true only when suggested_value and field_path are both set "
        "and the fix requires no human judgment.\n"
    )


def build_audit_user_prompt(profile_snapshot: dict) -> str:
    """Return the user prompt embedding the profile snapshot for analysis."""
    snapshot_text = json.dumps(profile_snapshot, indent=2, default=str)
    return (
        "Analyze the following Google Business Profile snapshot and return your recommendations "
        "as a JSON object matching the schema described in the system prompt.\n\n"
        f"Profile snapshot:\n{snapshot_text}\n\n"
        "Respond with valid JSON only. No markdown."
    )
