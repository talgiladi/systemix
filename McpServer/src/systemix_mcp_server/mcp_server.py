from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from systemix_mcp_server.config import Settings
from systemix_mcp_server.services import SystemixMcpService


logger = logging.getLogger(__name__)


def build_mcp_server(
    settings: Settings,
    service: SystemixMcpService,
) -> FastMCP:
    mcp = FastMCP(
        name=settings.app.name,
        instructions=(
            "Systemix support MCP server. "
            "All tools, prompts, and resources require user_id."
        ),
        stateless_http=True,
        json_response=True,
        streamable_http_path="/",
        log_level=settings.logging.level.upper(),
    )

    @mcp.tool()
    def get_account_details(user_id: str) -> dict[str, object]:
        """Return account details for the provided user_id."""
        logger.debug("Tool call: get_account_details", extra={"extra_fields": {"user_id": user_id}})
        return service.get_account_details(user_id)

    @mcp.tool()
    def get_technical_support(
        user_id: str,
        issue_type: str,
        summary: str,
        severity: str = "medium",
    ) -> dict[str, object]:
        """Return routing and troubleshooting details for a user support request."""
        logger.debug(
            "Tool call: get_technical_support",
            extra={
                "extra_fields": {
                    "user_id": user_id,
                    "issue_type": issue_type,
                    "severity": severity,
                }
            },
        )
        return service.get_technical_support(
            user_id=user_id,
            issue_type=issue_type,
            summary=summary,
            severity=severity,
        )

    @mcp.prompt()
    def technical_support_prompt(
        user_id: str,
        issue_summary: str,
        preferred_tone: str = "concise",
    ) -> str:
        """Generate a support-assistant prompt with account context."""
        logger.debug(
            "Prompt call: technical_support_prompt",
            extra={
                "extra_fields": {
                    "user_id": user_id,
                    "preferred_tone": preferred_tone,
                }
            },
        )
        return service.build_support_prompt(
            user_id=user_id,
            issue_summary=issue_summary,
            preferred_tone=preferred_tone,
        )

    @mcp.resource("account://{user_id}/profile")
    def account_profile(user_id: str) -> str:
        """Return a JSON account profile for the provided user_id."""
        logger.debug("Resource call: account_profile", extra={"extra_fields": {"user_id": user_id}})
        return service.get_account_resource(user_id)

    return mcp
