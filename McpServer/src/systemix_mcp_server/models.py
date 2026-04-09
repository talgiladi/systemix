from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AccountRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    account_id: str
    full_name: str
    email: str
    plan: str
    status: str
    region: str
    created_at: str
    last_login_at: str
    open_tickets: int = 0
    notes: list[str] = Field(default_factory=list)


class IssueRoute(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queue: str
    response_sla_hours: int
    recommended_steps: list[str] = Field(default_factory=list)


class SupportSettingsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    team_name: str = "Systemix Technical Support"
    default_queue: str = "general-support"
    default_response_sla_hours: int = 8
    issue_routes: dict[str, IssueRoute] = Field(default_factory=dict)


class KnowledgeBaseDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str
    title: str
    category: str
    content: str
    tags: list[str] = Field(default_factory=list)
    last_updated: date
