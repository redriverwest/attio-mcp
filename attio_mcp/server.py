import json
import logging

from mcp.server.fastmcp import FastMCP

from attio_mcp.attio_client import AttioClient
from attio_mcp.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("attio-mcp")

# Initialize Attio client
attio_client = AttioClient()


@mcp.tool()
async def search_companies(query: str, domain: str | None = None, limit: int = 10) -> str:
    """Search for companies in Attio CRM by name and optionally domain.

    Args:
        query: Company name to search for
        domain: Optional domain name for disambiguation (e.g., "openai.com")
        limit: Maximum number of results to return (default: 10)
    """
    try:
        result = await attio_client.search_companies(query=query, domain=domain, limit=limit)
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


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting Attio MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
