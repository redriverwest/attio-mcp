import json
import logging
from typing import Literal, cast

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

from attio_mcp.attio_client import AttioClient
from attio_mcp.auth import BearerTokenVerifier
from attio_mcp.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Type alias for log level
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Initialize authentication if token is configured
if settings.mcp_bearer_token:
    logger.info("Bearer token authentication enabled")
    token_verifier = BearerTokenVerifier()
    auth_settings = AuthSettings(
        issuer_url=cast(AnyHttpUrl, "https://attio-mcp.local"),
        resource_server_url=cast(AnyHttpUrl, "https://attio-mcp.local"),
        required_scopes=None,
    )
    mcp = FastMCP(
        "attio-mcp",
        token_verifier=token_verifier,
        auth=auth_settings,
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=cast(LogLevel, settings.log_level.upper()),
    )
else:
    logger.warning("Bearer token not configured - authentication disabled")
    mcp = FastMCP(
        "attio-mcp",
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=cast(LogLevel, settings.log_level.upper()),
    )

# Initialize Attio client
attio_client = AttioClient()


@mcp.tool()
async def search_companies(
    name: str | None = None,
    domain: str | None = None,
    limit: int = 15,
    owner_id: str | None = None,
    reminder_start: str | None = None,
    reminder_end: str | None = None,
) -> str:
    """Search for companies in Attio CRM by name, domain, and/or owner.

    Args:
        name: Optional company name substring to search for
        domain: Optional domain name for disambiguation (e.g., "openai.com")
        owner_id: Optional workspace member ID to filter by company owner
        reminder_start: Optional reminder start date (inclusive), format YYYY-MM-DD
        reminder_end: Optional reminder end date (inclusive), format YYYY-MM-DD
        limit: Maximum number of results to return (default: 15)
    """
    try:
        result = await attio_client.search_companies(
            name=name,
            domain=domain,
            owner_id=owner_id,
            reminder_start=reminder_start,
            reminder_end=reminder_end,
            limit=limit,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error searching companies: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def get_company_details(company_id: str) -> str:
    """Get detailed information about a specific company by record ID.

    Args:
        company_id: Unique record_id for the company (from search results or known ID)
    """
    try:
        result = await attio_client.get_company_details(company_id=company_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting company details: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def get_company_notes(company_id: str) -> str:
    """Get internal notes associated with a company.

    Args:
        company_id: Unique record_id for the company
    """
    try:
        result = await attio_client.get_company_notes(company_id=company_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting company notes: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def search_people(query: str, email: str | None = None, limit: int = 10) -> str:
    """Search for people in Attio CRM by name and optionally email.

    Args:
        query: Person name to search for
        email: Optional email for disambiguation (e.g., "john@example.com")
        limit: Maximum number of results to return (default: 10)
    """
    try:
        result = await attio_client.search_people(query=query, email=email, limit=limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error searching people: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def get_person_details(person_id: str) -> str:
    """Get detailed information about a specific person by record ID.

    Args:
        person_id: Unique record_id for the person (from search results or known ID)
    """
    try:
        result = await attio_client.get_person_details(person_id=person_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting person details: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def get_person_notes(person_id: str) -> str:
    """Get internal notes associated with a person.

    Args:
        person_id: Unique record_id for the person
    """
    try:
        result = await attio_client.get_person_notes(person_id=person_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting person notes: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def get_workspace_member(member_id: str) -> str:
    """Get detailed information about a workspace member.

    Args:
        member_id: Unique workspace_member_id (found in owner fields, interaction owner_actor, etc.)
    """
    try:
        result = await attio_client.get_workspace_member(member_id=member_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting workspace member: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def search_workspace_member_by_email(email: str) -> str:
    """Find a workspace member by their email address.

    Args:
        email: Email address to search for
    """
    try:
        result = await attio_client.list_workspace_members()
        members = result.get("data", [])
        for member in members:
            if member.get("email_address", "").lower() == email.lower():
                return json.dumps({"data": member}, indent=2)
        return json.dumps({"error": f"No workspace member found with email: {email}"})
    except Exception as e:
        logger.error(f"Error searching workspace member by email: {e}", exc_info=True)
        return f"Error: {str(e)}"


@mcp.tool()
async def list_workspace_members(limit: int = 100, contains: str | None = None) -> str:
    """List workspace members, optionally filtered by a substring match.

    Args:
        limit: Maximum number of members to return (default: 100)
        contains: Optional substring filter applied to full name and email address
    """
    try:
        result = await attio_client.list_workspace_members()
        members = result.get("data", [])

        if contains:
            needle = contains.lower()

            def matches(member: dict[str, object]) -> bool:
                first = str(member.get("first_name", "")).strip()
                last = str(member.get("last_name", "")).strip()
                email = str(member.get("email_address", "")).strip()
                full_name = f"{first} {last}".strip()
                return (
                    needle in first.lower()
                    or needle in last.lower()
                    or needle in full_name.lower()
                    or needle in email.lower()
                )

            members = [m for m in members if matches(m)]

        try:
            limit_int = int(limit)
        except (TypeError, ValueError) as e:
            raise ValueError("limit must be an integer") from e
        if limit_int < 0:
            raise ValueError("limit must be >= 0")

        return json.dumps({"data": members[:limit_int]}, indent=2)
    except Exception as e:
        logger.error(f"Error listing workspace members: {e}", exc_info=True)
        return f"Error: {str(e)}"


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting Attio MCP server...")

    if settings.mcp_transport == "sse":
        logger.info(
            "Running with transport=%s on %s:%s (mount_path=%s)",
            settings.mcp_transport,
            settings.mcp_host,
            settings.mcp_port,
            settings.mcp_mount_path,
        )
        mcp.run(transport="sse", mount_path=settings.mcp_mount_path)
    else:
        logger.info("Running with transport=%s", settings.mcp_transport)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
