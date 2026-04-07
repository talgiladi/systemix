from __future__ import annotations

import json
import logging
from collections.abc import Iterable

from systemix_mcp_server.config import Settings
from systemix_mcp_server.models import AccountRecord, IssueRoute


logger = logging.getLogger(__name__)


class AccountNotFoundError(LookupError):
    """Raised when the requested user account does not exist."""


class SystemixMcpService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._accounts_by_user_id = {
            record.user_id: record for record in settings.accounts.records
        }

    def get_account(self, user_id: str) -> AccountRecord:
        self._validate_user_id(user_id)
        account = self._accounts_by_user_id.get(user_id)
        if account is None:
            logger.warning(
                "Account lookup failed",
                extra={"extra_fields": {"user_id": user_id}},
            )
            raise AccountNotFoundError(f"No account found for user_id '{user_id}'.")

        logger.info(
            "Resolved account details",
            extra={
                "extra_fields": {
                    "user_id": user_id,
                    "account_id": account.account_id,
                    "plan": account.plan,
                    "status": account.status,
                }
            },
        )
        return account

    def get_account_details(self, user_id: str) -> dict[str, object]:
        account = self.get_account(user_id)
        return {
            "user_id": account.user_id,
            "account_id": account.account_id,
            "full_name": account.full_name,
            "email": account.email,
            "plan": account.plan,
            "status": account.status,
            "region": account.region,
            "created_at": account.created_at,
            "last_login_at": account.last_login_at,
            "open_tickets": account.open_tickets,
            "notes": account.notes,
        }

    def get_technical_support(
        self,
        user_id: str,
        issue_type: str,
        summary: str,
        severity: str = "medium",
    ) -> dict[str, object]:
        account = self.get_account(user_id)
        normalized_issue = issue_type.strip().lower()
        route = self._settings.support.issue_routes.get(normalized_issue) or self._default_route()
        case_id = f"SUP-{account.account_id}-{normalized_issue[:4].upper() or 'GEN'}"

        payload = {
            "case_id": case_id,
            "user_id": user_id,
            "account_id": account.account_id,
            "issue_type": normalized_issue,
            "severity": severity,
            "summary": summary.strip(),
            "assigned_queue": route.queue,
            "support_team": self._settings.support.team_name,
            "response_sla_hours": route.response_sla_hours,
            "recommended_steps": route.recommended_steps,
            "account_plan": account.plan,
            "open_tickets": account.open_tickets,
        }
        logger.info("Prepared technical support response", extra={"extra_fields": payload})
        return payload

    def build_support_prompt(
        self,
        user_id: str,
        issue_summary: str,
        preferred_tone: str = "concise",
    ) -> str:
        account = self.get_account(user_id)
        tone = preferred_tone.strip() or "concise"
        prompt = (
            f"You are assisting user {user_id} ({account.full_name}) on account {account.account_id}. "
            f"Use a {tone} tone. "
            f"Account plan: {account.plan}. Status: {account.status}. Region: {account.region}. "
            f"Open tickets: {account.open_tickets}. "
            f"User issue: {issue_summary.strip()}.\n"
            "Respond with:\n"
            "1. a short diagnosis\n"
            "2. next troubleshooting steps\n"
            "3. whether escalation is recommended"
        )
        logger.info(
            "Prepared prompt template",
            extra={
                "extra_fields": {
                    "user_id": user_id,
                    "preferred_tone": tone,
                    "account_id": account.account_id,
                }
            },
        )
        return prompt

    def get_account_resource(self, user_id: str) -> str:
        account = self.get_account(user_id)
        resource_payload = {
            "kind": "account_profile",
            "user_id": account.user_id,
            "account_id": account.account_id,
            "full_name": account.full_name,
            "email": account.email,
            "plan": account.plan,
            "status": account.status,
            "region": account.region,
            "notes": list(account.notes),
        }
        logger.info(
            "Prepared account resource",
            extra={
                "extra_fields": {
                    "user_id": user_id,
                    "account_id": account.account_id,
                }
            },
        )
        return json.dumps(resource_payload, indent=2)

    def known_user_ids(self) -> list[str]:
        return sorted(self._accounts_by_user_id.keys())

    def issue_types(self) -> Iterable[str]:
        return sorted(self._settings.support.issue_routes.keys())

    @staticmethod
    def _validate_user_id(user_id: str) -> None:
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required for every MCP call.")

    def _default_route(self) -> IssueRoute:
        return IssueRoute(
            queue=self._settings.support.default_queue,
            response_sla_hours=self._settings.support.default_response_sla_hours,
            recommended_steps=[
                "Capture the exact user action that triggered the problem.",
                "Attach logs or screenshots if available.",
                "Escalate if production impact is ongoing.",
            ],
        )
