"""Attio API client for interacting with Attio CRM."""

import logging
from typing import Any, cast

import httpx

from attio_mcp.config import settings

logger = logging.getLogger(__name__)


class AttioClient:
    """Client for interacting with the Attio API."""

    def __init__(self) -> None:
        """Initialize the Attio client."""
        self.base_url = settings.attio_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.attio_api_key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_search_payload(
        self,
        name_filter: dict[str, Any],
        optional_filter: dict[str, Any] | None,
        limit: int,
    ) -> dict[str, Any]:
        """
        Build a search query payload with filters.

        Args:
            name_filter: The primary name filter (e.g., {"name": {"$contains": "query"}})
            optional_filter: Optional secondary filter (e.g., domain or email filter)
            limit: Maximum number of results

        Returns:
            Payload dictionary ready for the query endpoint
        """
        filters = [name_filter]
        if optional_filter:
            filters.append(optional_filter)

        payload: dict[str, Any] = {"limit": limit}
        if len(filters) > 1:
            payload["filter"] = {"$and": filters}
        else:
            payload["filter"] = filters[0]

        return payload

    async def _get_notes(
        self, parent_object: str, parent_record_id: str, entity_name: str
    ) -> dict[str, Any]:
        """
        Get notes for a parent object (company or person).

        Args:
            parent_object: The object type ("companies" or "people")
            parent_record_id: The record ID of the parent
            entity_name: Human-readable name for logging ("company" or "person")

        Returns:
            Dictionary containing notes data
        """
        logger.info(f"Getting {entity_name} notes for ID: {parent_record_id}")

        try:
            params = {
                "parent_object": parent_object,
                "parent_record_id": parent_record_id,
            }
            response = await self.client.get("/notes", params=params)
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(
                f"Retrieved {len(data.get('data', []))} notes for {entity_name} {parent_record_id}"
            )
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"No notes found for {entity_name}: {parent_record_id}")
                return {"data": []}
            logger.error(
                f"HTTP error getting {entity_name} notes: "
                f"{e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error getting {entity_name} notes: {e}", exc_info=True)
            raise

    async def search_companies(
        self, query: str, domain: str | None = None, limit: int = 10
    ) -> dict[str, Any]:
        """
        Search for companies in Attio by name and optionally domain.

        Args:
            query: Company name to search for
            domain: Optional domain name for disambiguation (e.g., "openai.com")
            limit: Maximum number of results to return

        Returns:
            Dictionary containing search results with company records
        """
        logger.info(f"Searching companies: query={query}, domain={domain}, limit={limit}")

        name_filter = {"name": {"$contains": query}} if query else {}
        domain_filter = {"domains": {"domain": {"$eq": domain}}} if domain else None
        payload = self._build_search_payload(name_filter, domain_filter, limit)

        try:
            response = await self.client.post("/objects/companies/records/query", json=payload)
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(f"Found {len(data.get('data', []))} companies for query '{query}'")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error searching companies: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error searching companies: {e}", exc_info=True)
            raise

    async def get_company_details(self, company_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific company by record ID.

        Args:
            company_id: Unique record_id for the company
                (e.g., "0000f69b-511f-4321-ac32-3e4c2c93894c")

        Returns:
            Dictionary containing full company record with all attributes
        """
        logger.info(f"Getting company details for ID: {company_id}")

        try:
            response = await self.client.get(f"/objects/companies/records/{company_id}")
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(f"Successfully retrieved company details for ID: {company_id}")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Company not found with ID: {company_id}")
                raise Exception(f"Company not found: {company_id}") from e
            logger.error(
                f"HTTP error getting company details: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error getting company details: {e}", exc_info=True)
            raise

    async def get_company_notes(self, company_id: str) -> dict[str, Any]:
        """
        Get notes associated with a company.

        Args:
            company_id: Unique record_id for the company

        Returns:
            Dictionary containing notes associated with the company
        """
        return await self._get_notes("companies", company_id, "company")

    async def search_people(
        self, query: str, email: str | None = None, limit: int = 10
    ) -> dict[str, Any]:
        """
        Search for people in Attio by name and optionally email.

        Args:
            query: Person name to search for
            email: Optional email for disambiguation (e.g., "john@example.com")
            limit: Maximum number of results to return

        Returns:
            Dictionary containing search results with person records
        """
        logger.info(f"Searching people: query={query}, email={email}, limit={limit}")

        name_filter = {"name": {"$contains": query}} if query else {}
        email_filter = {"email_addresses": {"email_address": {"$eq": email}}} if email else None
        payload = self._build_search_payload(name_filter, email_filter, limit)

        try:
            response = await self.client.post("/objects/people/records/query", json=payload)
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(f"Found {len(data.get('data', []))} people for query '{query}'")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error searching people: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error searching people: {e}", exc_info=True)
            raise

    async def get_person_details(self, person_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific person by record ID.

        Args:
            person_id: Unique record_id for the person

        Returns:
            Dictionary containing full person record with all attributes
        """
        logger.info(f"Getting person details for ID: {person_id}")

        try:
            response = await self.client.get(f"/objects/people/records/{person_id}")
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(f"Successfully retrieved person details for ID: {person_id}")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Person not found with ID: {person_id}")
                raise Exception(f"Person not found: {person_id}") from e
            logger.error(
                f"HTTP error getting person details: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error getting person details: {e}", exc_info=True)
            raise

    async def get_person_notes(self, person_id: str) -> dict[str, Any]:
        """
        Get notes associated with a person.

        Args:
            person_id: Unique record_id for the person

        Returns:
            Dictionary containing notes associated with the person
        """
        return await self._get_notes("people", person_id, "person")

    async def get_workspace_member(self, member_id: str) -> dict[str, Any]:
        """
        Get detailed information about a workspace member.

        Args:
            member_id: Unique workspace_member_id (found in owner fields,
                interaction owner_actor, etc.)

        Returns:
            Dictionary containing workspace member details including:
            first_name, last_name, email_address, avatar_url, access_level
        """
        logger.info(f"Getting workspace member details for ID: {member_id}")

        try:
            response = await self.client.get(f"/workspace_members/{member_id}")
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(f"Successfully retrieved workspace member details for ID: {member_id}")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Workspace member not found with ID: {member_id}")
                raise Exception(f"Workspace member not found: {member_id}") from e
            logger.error(
                f"HTTP error getting workspace member: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error getting workspace member: {e}", exc_info=True)
            raise

    async def list_workspace_members(self) -> dict[str, Any]:
        """
        List all workspace members.

        Returns:
            Dictionary containing array of workspace member objects
        """
        logger.info("Listing all workspace members")

        try:
            response = await self.client.get("/workspace_members")
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

            logger.info(f"Retrieved {len(data.get('data', []))} workspace members")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error listing workspace members: "
                f"{e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error listing workspace members: {e}", exc_info=True)
            raise
