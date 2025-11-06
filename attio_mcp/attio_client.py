"""Attio API client for interacting with Attio CRM."""

import logging
from typing import Any

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

        # Build filter conditions
        filters = []

        # Always search by name using $contains for partial matching
        if query:
            filters.append({"name": {"$contains": query}})

        # Optionally filter by domain for disambiguation
        if domain:
            filters.append({"domains": {"domain": {"$eq": domain}}})

        # Construct the payload
        payload: dict[str, Any] = {"limit": limit}

        if filters:
            # Use $and if multiple filters, otherwise use single filter
            if len(filters) > 1:
                payload["filter"] = {"$and": filters}
            else:
                payload["filter"] = filters[0]

        try:
            response = await self.client.post("/objects/companies/records/query", json=payload)
            response.raise_for_status()
            data = response.json()

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
            data = response.json()

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
        logger.info(f"Getting company notes for ID: {company_id}")

        try:
            # Query notes endpoint with company as parent object
            params = {
                "parent_object": "companies",
                "parent_record_id": company_id,
            }
            response = await self.client.get("/notes", params=params)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Retrieved {len(data.get('data', []))} notes for company {company_id}")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"No notes found for company: {company_id}")
                # Return empty notes list for 404 (not found is not an error for notes)
                return {"data": []}
            logger.error(
                f"HTTP error getting company notes: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error getting company notes: {e}", exc_info=True)
            raise

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

        # Build filter conditions
        filters = []

        # Always search by name using $contains for partial matching
        if query:
            filters.append({"name": {"$contains": query}})

        # Optionally filter by email for disambiguation
        if email:
            filters.append({"email_addresses": {"email_address": {"$eq": email}}})

        # Construct the payload
        payload: dict[str, Any] = {"limit": limit}

        if filters:
            # Use $and if multiple filters, otherwise use single filter
            if len(filters) > 1:
                payload["filter"] = {"$and": filters}
            else:
                payload["filter"] = filters[0]

        try:
            response = await self.client.post("/objects/people/records/query", json=payload)
            response.raise_for_status()
            data = response.json()

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
            data = response.json()

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
        logger.info(f"Getting person notes for ID: {person_id}")

        try:
            # Query notes endpoint with person as parent object
            params = {
                "parent_object": "people",
                "parent_record_id": person_id,
            }
            response = await self.client.get("/notes", params=params)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Retrieved {len(data.get('data', []))} notes for person {person_id}")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"No notes found for person: {person_id}")
                # Return empty notes list for 404 (not found is not an error for notes)
                return {"data": []}
            logger.error(
                f"HTTP error getting person notes: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attio API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Error getting person notes: {e}", exc_info=True)
            raise
